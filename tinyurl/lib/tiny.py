import hashlib
import logging
import time
import random

from tinyurl.models import Url

# enable logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

try:
    import redis
except ModuleNotFoundError:
    logging.error("Redis module missing")

try:
    g_redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
except NameError:
    g_redis = None


class UrlHandler():

    @staticmethod
    def get_tinyurl(user, originalurl, suggested_url):
        """Given a url, return tinyurl, create if necessary.
        Args:
            originalurl: url to shorten.

        Returns:
            Returns short url
        """

        logging.debug("Creating short url for {}".format(originalurl))
        start = time.time()
        db_obj = UrlHandler._get_or_create_in_db(user, originalurl, suggested_url)
        end = time.time()
        logging.info("Tinurl created {} in {} in seconds".format(db_obj.shorturl, end - start))
        return db_obj.shorturl

    @staticmethod
    def _get_or_create_in_db(user, originalurl, suggested_url):
        """
        Helper function to get or create tiny url
        Generates 32 bit md5 hash and returns right most 6 characters as tiny url code
        In case of collision, it shifts left through the md5 hash until an available 6 character window is found
        Args:
            originalurl: The url to shorten.

        Returns:
            Returns short url
        """

        if not (Url.objects.filter(user__username__exact=user.get_username(), originalurl=originalurl)):
            if len(suggested_url) == 0:
                md5hash = hashlib.md5(originalurl.encode('utf-8')).hexdigest()
                shorturl = md5hash[-6:] + str(random.randint(1, 99))
                obj = Url.objects.create(user=user, shorturl=shorturl, originalurl=originalurl)

                # handle collisions, make 10 attempts
                # shift left through the md5 if the 6 character code chosen so far is taken by a different url
                max_tries = 1
                while obj.originalurl != originalurl and max_tries <= 10:
                    shorturl = md5hash[-6 - max_tries:-max_tries] + str(random.randint(1, 99))
                    obj = Url.objects.create(user=user, shorturl=shorturl, originalurl=originalurl)
                    logging.info('Collision occured, {} resolution attempts so far'.format(max_tries))
                    max_tries += 1
            else:
                obj = Url.objects.create(user=user, shorturl=suggested_url, originalurl=originalurl)

        else:
            obj = Url.objects.get(user=user, originalurl=originalurl)
        return obj

    @staticmethod
    def get_originalurl(request, tinurl):
        """
        Fetch original url
        Looks up the tinyurl code in Redis cache before going to Postgres database
        Args:
            tinurl: tiny url code.

        Returns:
            Returns the orginal url
        """
        logging.debug("Original url requested for {}".format(tinurl))

        # attempt to lookup  Redis cache
        start = time.time()
        originalurl = UrlHandler.redis_get(tinurl)

        if originalurl:
            Url.objects.create(user=request.user, shorturl=tinurl, originalurl=originalurl, device=(
                True if request.user_agent.is_pc else False), browser=request.user_agent.browser.family)
            logging.info("Cache hit. Redis returned url {} in {} seconds".format(originalurl, time.time() - start))
            return originalurl

        logging.info("Cache miss for {}".format(tinurl))
        # not in Redis, fetch from database
        url = None
        try:
            url = Url.objects.get(shorturl=tinurl)
            # cache the response
            UrlHandler.redis_set(tinurl, url.originalurl)
            Url.objects.create(user=request.user, shorturl=tinurl, originalurl=url.originalurl, device=(
                True if request.user_agent.is_pc else False), browser=request.user_agent.browser.family)

        except Url.DoesNotExist:
            logging.error("Invalid url code")
            return None

        logging.info("Postgres returned url {} in {} seconds".format(url.originalurl, time.time() - start))

        return url.originalurl

    @staticmethod
    def redis_get(key):
        global g_redis
        if g_redis:
            return g_redis.get(key)
        else:
            return None

    @staticmethod
    def redis_set(key, value):
        global g_redis
        if g_redis:
            g_redis.set(key, value)
