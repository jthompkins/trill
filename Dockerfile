FROM fedora:latest

RUN dnf install -y \
    https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
    https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm \
    && dnf install -y ffmpeg \
    && python3 -m ensurepip --default-pip \
    && python3 -m pip install youtube_dl \
    && python3 -m pip install -U discord.py[voice] \
    && mkdir -p /usr/threedogbot/ \

WORKDIR /usr/threedogbot

COPY ./threedog.py ./threedog_bot_constants.py records sounds voicelines /usr/threedogbot/

#To be combined with the above run commands. This is for testing only
RUN python3 -m pip install mutagen \
    && python3 -m pip install bs4


RUN chgrp -R 0 /usr/threedogbot/ \
    && chmod -R g=u /usr/threedogbot/ 



USER 1001

CMD ["python3","/usr/threedogbot/threedog.py"]
