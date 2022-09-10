import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from .keywords_utils import tagss as keyword_tagss
from .caption_utils import tagss as caption_tagss


class KeywordToTags(APIView):
    def get(self, request, *args, **kwargs):
        try:
            """
            This API generates most trending hashtags on basis given keyword
            """
            keyword = self.request.GET.get("keyword")
            if keyword:
                hashtag = keyword_tagss(keyword)
                return Response({"success": True, "hashtags": hashtag})
            else:
                logging.info(
                    "================================================================"
                )
                logging.info(
                    "Keyword Not Found: Please provide keyword for generating hashtag"
                )
                logging.info(
                    "================================================================"
                )
                return Response(
                    {
                        "success": False,
                        "Message": "Keyword Not Found: Please provide keyword for generating hashtag",
                    }
                )
        except Exception as e:
            logging.info("=====================================")
            logging.info("Exception: " + str(e))
            logging.info("=====================================")
            return Response({"success": False, "Message": str(e)})


class CaptionToTags(APIView):
    def get(self, request, *args, **kwargs):
        try:
            """
            This API generates most similar hashtags on basis of given caption
            """
            caption = self.request.GET.get("caption")
            if caption:
                hashtag = caption_tagss(caption)
                return Response({"success": True, "hashtags": hashtag})
            else:
                logging.info(
                    "================================================================"
                )
                logging.info(
                    "Caption Not Found: Please provide keyword for generating hashtag"
                )
                logging.info(
                    "================================================================"
                )

                return Response(
                    {
                        "success": False,
                        "Message": "Caption Not Found: Please provide keyword for generating hashtag",
                    }
                )
        except Exception as e:
            logging.info("=====================================")
            logging.info("Exception: " + str(e))
            logging.info("=====================================")
            return Response({"success": False, "Message": str(e)})
