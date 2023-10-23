# Escaux-Grapher

Extract data and build Gephi Graphs from Escaux SMP


## Installation	

Install [Git cmd](https://git-scm.com/downloads)

Install [Pyhton 3](https://www.python.org/downloads/)
(don't forget to check the 'add to path' option)

Install [Gephi viz](https://gephi.org/)

Install [DBeaver Community](https://dbeaver.io/download/)

Open CMD and Clone Git Repository 
``` bash
git clone https://github.com/MinerBigWhale/Escaux-Grapher.git && cd Escaux-Grapher
```
Install Python requirements
``` bash
pip install -r .\requirements.txt
```

Create config files from sample files


 * config.ini
``` ini
[files]
chromedriver = chromedriver-win64\chromedriver.exe
tempfolder = temp\
invoices = invoices\
database = temp\db.sqlite

[website]
login = https://stable-4.smptel.irisnet.be/
phonesop1 = https://stable-4.smptel.irisnet.be/smp/00000001/phones_overview.php
phonesop2 = https://stable-4.smptel.irisnet.be/smp/00000002/phones_overview.php
directory = https://stable-4.smptel.irisnet.be/smp/00000000/import_directory.php
ddi = https://stable-4.smptel.irisnet.be/smp/00000000/import_ddis.php
phone = https://stable-4.smptel.irisnet.be/smp/00000000/import_resources.php?type=phone
queue = https://stable-4.smptel.irisnet.be/smp/00000000/import_resources.php?type=queue
netconsole = https://stable-4.smptel.irisnet.be/smp/00000000/import_resources.php?type=client
fmu = https://stable-4.smptel.irisnet.be/smp/00000000/run_app.php?id=47173&async=0&fmu=1&extension=ID

[delay]
cooldown = 1
maxwait = 20
```

ensure you replaced 00000000 by your SMP Master SOPKey, 00000001 by your Primary SOPKey, and 00000002 by your Backup SOPKey.

* credentials.json
``` json 
{
    "username": "user@escaux.be",
    "password": "pass"
}
```

## Usage

Run the main script to Build the DB
``` bash
Python Main.py
```

You can explore the DB Using DBeaver and adding a connection to the SQLite DB File in the temp forlder.

You can also import the db in Gephi, 
use this query for nodes 
``` SQL
SELECT id, "type", description as label FROM extension
```
and this query for links
``` SQL
SELECT id, origin as source, destination as target, description as "type", description  as label FROM redirection 
```