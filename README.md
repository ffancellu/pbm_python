# Vagrant

```
#!bash

vagrant up
fab vagrant server_update update_virtualbox server_reboot fix_vagrant_guest_additions
fab vagrant install_tools
fab vagrant build upload_source_code start_servers

```

