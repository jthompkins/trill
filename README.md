#Trill Bot

A Discord bot that can play music.

20220723 - Renamed to Trill

20200127 - Need to update code to work with new changes to Discord API. Need to refactor large portions of code.

20200220 - Removed bot code and replaced with environment variable pull. If ran in a container the environment variable TRILLBOT needs to be set to the key for the bot.

20200221 - Major refactoring of code due to Discord Python API changes.



Installing FFMPEG

FFMPEG is needed to play audio.

On RHEL 8:

yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

yum localinstall --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-8.noarch.rpm https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-8.noarch.rpm

yum install -y ffmpeg ffmpeg-devel
