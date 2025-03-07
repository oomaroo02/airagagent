# Releases notes
- 2025-03-07: 
    - Upgraded libreoffice to 2.8.4.5
    - LibreOffice (.doc, . docx, .ppt, .pttx -> pdf) if not installed default to default parser
    - Catch errors if the streaming cursor is expired and recreate the connection (ex: when document understanding takes too much time, the streaming connection expires)
    
- 2025-02-19: 
    - Fix for non-latin1 files and customized_url_source 
    - LibreOffice (.doc, . docx, .ppt, .pttx -> pdf) enabled as default
    - Chrome+Selenium enabled enabled as default 
    - Remove the auth_token and replace by oci raw-request

## OCI-Starter
### Usage 

### Commands
- starter.sh help    : Show the list of commands
- starter.sh build   : Build the whole program: Run Terraform, Configure the DB, Build the App, Build the UI
- starter.sh destroy : Destroy the objects created by Terraform
- starter.sh env     : Set the env variables in BASH Shell
                    
### Directories
- src           : Sources files
    - app       : Source of the Backend Application 
    - ui        : Source of the User Interface 
    - db        : SQL files of the database
    - terraform : Terraform scripts

Help (Tutorial + How to customize): https://www.ocistarter.com/help

### Next Steps:
- Edit the file env.sh. Some variables need to be filled:
```
export TF_VAR_db_password="__TO_FILL__"
export TF_VAR_auth_token="__TO_FILL__"
```

- Run:
  cd agent
  ./starter.sh build
