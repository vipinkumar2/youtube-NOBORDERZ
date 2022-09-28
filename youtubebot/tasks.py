from log import LOGGER
from background_task import background
import random
import time
import logging
from youtubebot.models import YoutubeJob, YoutubeAccount
from youtubebot.utils import (
    video_like,
    comment_on_video,
    subscribe_channel,
    video_dislike,
    views_video,
    video_upload,
    time_sleep,
)


@background(queue="yt_job")
def like_video_yt(job_id):
    jobs = YoutubeJob.objects.get(id=job_id)
    jobs.status = "I"
    jobs.save()
    try:
        if jobs.group:
            members = YoutubeAccount.objects.filter(group=jobs.group)
            like_status = {}
            for member in members:
                wait = time_sleep()
                time.sleep(wait)
                obj = video_like(member.credentials, jobs.video_url)
                like_status[member.email] = obj
                jobs.status="I"
                jobs.save()
            jobs.group_status = like_status
            jobs.status="C"
            jobs.save()
            print("Like job completed")
            logging.info("=====================  video like success using group==============================")
        else:
            wait = time_sleep()
            time.sleep(wait)
            members = YoutubeAccount.objects.filter(id=jobs.accounts.id).first()
            obj = video_like(members.credentials, jobs.video_url)
            if obj:
                jobs.status="C"
                jobs.save()
                logging.info("=====================  video like success using account==============================")
            else:
                jobs.status="F"
                jobs.save()
                logging.info("=====================  video like failed using account==============================")

    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()


@background(queue="yt_job")
def comment_video_yt(job_id):
    jobs = YoutubeJob.objects.get(id=job_id)
    jobs.status="I"
    jobs.save()
    comments = ['nice', 'thats great', 'Great tips', 'very nice', 'sound great', 'good', 'good job']
    comment = random.choice(comments)
    try:
        if jobs.group:
            members = YoutubeAccount.objects.filter(group=jobs.group)
            comment_status = {}
            for member in members:
                wait = time_sleep()
                time.sleep(wait)
                obj = comment_on_video(member.credentials, jobs.video_url, comment)
                comment_status[member.email] = obj
                jobs.status="I"
                jobs.save()
            jobs.group_status = comment_status
            jobs.status="C"
            jobs.save()
            logging.info("=====================  video comment success using group==============================")
        else:
            wait = time_sleep()
            time.sleep(wait)
            members = YoutubeAccount.objects.filter(id=jobs.accounts.id).first()
            obj = comment_on_video(members.credentials, jobs.video_url, comment)
            if obj:
                jobs.status="C"
                jobs.save()
                logging.info("=====================  video comment success using account==============================")
            else:
                jobs.status="F"
                jobs.save()
                logging.info("=====================  video comment failed using account==============================")
    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()


@background(queue="yt_job")
def dislike_video_yt(job_id):
    jobs = YoutubeJob.objects.get(id=job_id)
    jobs.status="I"
    jobs.save()
    try:
        if jobs.group:
            members = YoutubeAccount.objects.filter(group=jobs.group)
            dislike_status = {}
            for member in members:
                wait = time_sleep()
                time.sleep(wait)
                obj = video_dislike(member.credentials, jobs.video_url)
                dislike_status[member.email] = obj
                jobs.status="I"
                jobs.save()
            jobs.group_status = dislike_status
            jobs.status="C"
            jobs.save()
            LOGGER.info("=====================  video dislike success using group==============================")
        else:
            wait = time_sleep()
            time.sleep(wait)
            members = YoutubeAccount.objects.filter(id=jobs.accounts.id).first()
            obj = video_dislike(members.credentials, jobs.video_url)
            if obj:
                jobs.status="C"
                jobs.save()
                logging.info("=====================  video dislike success using account==============================")
            else:
                jobs.status="F"
                jobs.save()
                logging.info("=====================  video dislike failed using account==============================")
    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()


@background(queue="yt_job")
def sunscribe_channel_yt(job_id,schedule="", verbose_name="", creator=""):
    jobs = YoutubeJob.objects.get(id=job_id)
    jobs.status="I"
    jobs.save()
    try:
        if jobs.group:
            members = YoutubeAccount.objects.filter(group=jobs.group)
            subscribe_status = {}
            for member in members:
                wait = time_sleep()
                time.sleep(wait)
                obj = subscribe_channel(member.credentials, jobs.channel_id)
                subscribe_status[member.email] = obj
            jobs.group_status = subscribe_status
            jobs.status="C"
            jobs.save()
            logging.info("=====================  channel subscribe success using group==============================")
        else:
            wait = time_sleep()
            time.sleep(wait)
            members = YoutubeAccount.objects.filter(id=jobs.accounts.id).first()
            obj = subscribe_channel(members.credentials, jobs.channel_id)
            if obj:
                jobs.status="C"
                jobs.save()
                logging.info("=====================  channel subscribe success using account==============================")
            else:
                jobs.status="F"
                jobs.save()
                logging.info("=====================  video subscribe failed using account==============================")
    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()

# @background(queue="yt_job")
def send_veiw(video_url, video_views):
    views_video(video_url, video_views)
    