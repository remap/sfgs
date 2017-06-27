# Search for Global Song

This is a code repo of "Future of Storytelling", year 3 project.

## EDL Engine

EDL engine is used from within TouchDesigner to process incoming EDL edit events and perform video rendering accordingly.

## How to run TouchDesigner project

- Boot windows
- Go to *“C:\sfgs”* folder
- Setup NTP sync:
    - Double-click *“ntp-local”* bat file, this will run script for syncing windows clock with the remote machine 
       - > Remote machine must be up and running, this is the ubuntu machine in 1469B
- Go to *“C:\sfgs\touch\project”*
- Open *sfgs.toe* (it should be opened in 32bit TouchDesigner, since YoutubeTOP works for 32bit only)
- Switch to preview mode by pressing F1
- Make sure *“Auto-write”* button is enabled
    - > *“Write to file”* should be disabled, it’ll be enabled automatically when video starts
- Enter publisher’s IP address in *“Publisher IP”* field and press “Reset”
    - > “Status” should turn green and say “Connected”
- Start publisher
    - > Video will be automatically saved in “C:\Users\remapfos-1\assemblyXX.mov” where XX - incrementally increasing index. alongside video, three log files will be saved:
      >  - events-incoming.log — logging of all events received from publisher
      >  - events-processed.log — logging of all processed events (that affect playback) 
      >  - op-timeline.log — low-level logging of audio/video playback/dispatch commands on the timeline
