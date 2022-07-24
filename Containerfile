FROM fedora:latest

RUN dnf install -y \
    https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
    https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm \
    && dnf install -y ffmpeg \
    && python3 -m ensurepip --default-pip \
    && python3 -m pip install youtube_dl \
    && python3 -m pip install -U discord.py[voice] \
    && mkdir -p /usr/trillbot/ \

WORKDIR /usr/trillbot

COPY ./trill.py ./trill_bot_constants.py records sounds voicelines /usr/trillbot/

#To be combined with the above run commands. This is for testing only
RUN python3 -m pip install mutagen \
    && python3 -m pip install bs4


RUN chgrp -R 0 /usr/trillbot/ \
    && chmod -R g=u /usr/trillbot/ 



USER 1001

CMD ["python3","/usr/trillbot/src/__main__.py"]
