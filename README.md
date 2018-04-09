# KnoraJSONTestImport

The provided python script allows you to import JSON test data to Knora. JSON file content must follow the content required by the Knora API (POST v1/resources endpoint).

## Python 3 + requests

Create env for python3 if default python version is python2 and install requests package:

```unix
$ python --version
Python 2.7.10
$ python3 --version
Python 3.6.4
$ python3 -m venv python3-env
$ source python3-env/bin/activate
$ python --version
Python 3.6.4
$ pip install requests
$ ./ImportData.py
Usage: ./ImportData.py <config.json> <data_folder>
$ deactivate
```

## Usage

`./ImportData.py <config.json> <data_folder>`

## Config

config.json example:

```json
{
  "url": "http://0.0.0.0:3333/",
  "email": "xxxx",
  "password": "xxxx"
}
```

## Data folder

Must contain one folder per class and one file per object. Folders and files are scanned in alphanumeric order to provide object dependencies order. IRI `link_value` will be resolved during import, set dependency to other objects as follow:

```json
{
        "link_value":
          "<%00.Image/002.json%>"
}
```

`<%00.Image/002.json%>` will be replaced by the IRI of the created object of file `00.Image/002.json`.

To associate an image (stored in Sipi) to an object (subclass of `StillImageRepresentation`), image file must have the same name of the object file (supported extensions: .png and .jpg).

Data folder example of LL ontology:

```unix
data
├── 00.Image          (Image class folder)
│   ├── 001.jpg       (Image related to data of 001.json)
│   ├── 001.json      (Image data of an object)
└── 01.FreeContent    (FreeContent class folder)
    └── 001.json      (FreeContent data of an object)
```

## Test

```unix
$ ./ImportData.py config.json data/

- Load config file: /Users/gfaucher/work/projects/lumieres/LL2018/data-test/config.json
   * url: http://0.0.0.0:3333/
   * email: xxxxx
   * password: xxxxx

- Login
   * token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJhcGkiLCJzdWIiOiJodHRwOi8vcmRmaC5jaC91c2Vycy9yb290IiwiYXVkIjoid2ViYXBpIiwiaWF0IjoxNTIyOTQ3MTY4LCJleHAiOjE1MjU1MzkxNjgsImp0aSI6IjkzMWJiMzc3LWQ1MGMtNDlmOS05YTA0LWM2NTI1YzE3ZmI0NyJ9.yvydSIYpeIFXHEnyrBB5qMOgMVaCBZqAv2b6tPHr2es

- Send data from folder /Users/gfaucher/work/projects/lumieres/KnoraJSONTestImport/data

 => 00.Image

   -> 001.json
   -> related image /Users/gfaucher/work/projects/lumieres/KnoraJSONTestImport/data/00.Image/001.jpg
   -> <Response [200]> | Created object 00.Image/001.json iri=http://rdfh.ch/0113/lumieres-lausanne/2n2YGPe7QGCbhTtn_WUVjQ

 => 01.FreeContent

   -> 001.json
   -> resolved link 00.Image/001.json into http://rdfh.ch/0113/lumieres-lausanne/2n2YGPe7QGCbhTtn_WUVjQ
   -> <Response [200]> | Created object 01.FreeContent/001.json iri=http://rdfh.ch/0113/lumieres-lausanne/q4jex-SLREqZB7eJCFEWig

- Done: created 2 objects and added 1 images [1.3345389366149902 s]

```
