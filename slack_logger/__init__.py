import requests
from django.conf import settings


def send_log(log_type, error=""):
    """
    sends error log to slack channel
    :param log_type: info, error, exception etc
    :param error: error/exception trace
    :return: post the error to python_logs channel
    """
    if settings.SEND_LOG_TO_SLACK:
        data = {"text": "%s:-%s" % (log_type, error)}
        response = requests.post(
            url='https://hooks.slack.com/services/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', json=data
        )

        print(response.text)
    return True


def send_log_user_stats(log_type, msg=""):
    """
        sends error log to slack channel
        :param log_type: info, error, exception etc
        :param error: error/exception trace
        :return: post the error to python_logs channel
        """
    if settings.SEND_LOG_TO_SLACK:
        data = {"text": "%s:-%s" % (log_type, msg)}
        response = requests.post(
            url='https://hooks.slack.com/services/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', json=data
        )

        print(response.text)
    return True


#
# @app.task
# def send_slack_stat(msg, channel=None):
#     """
#     :param msg: Data to post in channel
#     :param channel: slack channel
#     :return: POST data to channel
#     """
#     if not msg:
#         return False
#     data = {
#         "text": msg,
#     }
#
#     if channel == 'Company':
#         response = requests.post(
#             url='https://hooks.slack.com/services/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', json=data
#         )
#
#     if channel == 'China':
#         pass
#         # response = requests.post(
#         #     url='https://hooks.slack.com/services/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', json=data
#         # )
#         # add_logger(
#         #     "info",
#         #     "channel_stats",
#         #     "slack_logger",
#         #     "send_slack_stat",
#         #     "response",
#         #     """
#         #     channel: {},
#         #     data: {},
#         #     status_code: {}
#         #     response: {}
#         #     """.format(channel, data, response.status_code, response.text)
#         # )
#     if channel == 'Korea':
#         pass
#     #     response = requests.post(
#     #         url='https://hooks.slack.com/services/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', json=data
#     #     )
#     #     add_logger(
#     #         "info",
#     #         "channel_stats",
#     #         "slack_logger",
#     #         "send_slack_stat",
#     #         "response",
#     #         """
#     #         channel: {},
#     #         data: {},
#     #         status_code: {}
#     #         response: {}
#     #         """.format(channel, data, response.status_code, response.text)
#     #     )
#     if channel == 'Vietnam':
#         pass
#         # response = requests.post(
#         #     url='https://hooks.slack.com/services/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', json=data
#         # )
#         # add_logger(
#         #     "info",
#         #     "channel_stats",
#         #     "slack_logger",
#         #     "send_slack_stat",
#         #     "response",
#         #     """
#         #     channel: {},
#         #     data: {},
#         #     status_code: {}
#         #     response: {}
#         #     """.format(channel, data, response.status_code, response.text)
#         # )
#     if channel == 'ANV':
#         pass
#         # response = requests.post(
#         #     url='https://hooks.slack.com/services/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', json=data
#         # )
#         # add_logger(
#         #     "info",
#         #     "channel_stats",
#         #     "slack_logger",
#         #     "send_slack_stat",
#         #     "response",
#         #     """
#         #     channel: {},
#         #     data: {},
#         #     status_code: {}
#         #     response: {}
#         #     """.format(channel, data, response.status_code, response.text)
#         # )
#     if channel == 'ANT':
#         pass
#         # response = requests.post(
#         #     url='https://hooks.slack.com/services/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', json=data
#         # )
#         # add_logger(
#         #     "info",
#         #     "channel_stats",
#         #     "slack_logger",
#         #     "send_slack_stat",
#         #     "response",
#         #     """
#         #     channel: {},
#         #     data: {},
#         #     status_code: {}
#         #     response: {}
#         #     """.format(channel, data, response.status_code, response.text)
#         # )
#     # if channel == 'Gaming':
#     #     response = requests.post(
#     #         url='https://hooks.slack.com/services/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', json=data
#     #   )
#
#     if channel == "Security":
#         response = requests.post(
#             url='https://hooks.slack.com/services/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', json=data
#         )
#
#     if channel == "Saintkingdom":
#         response = requests.post(
#             url='https://hooks.slack.com/services/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', json=data
#         )
#
#
#     if channel == "Xigolo":
#         response = requests.post(
#             url='https://hooks.slack.com/services/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', json=data
#         )
#
#
#     return True
#
#
# def send_touku_stats(log_type, error=""):
#     data = {"text": "%s:-%s" % (log_type, error)}
#     response = requests.post(
#             url='https://hooks.slack.com/services/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', json=data
#         )
#     return True
#
