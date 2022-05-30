# Sample Container App

This repository made for the purpose of testing the cluster indivduals (like database and etc.) connections and behavior, simple as it is.

## Build

```
$ docker build -t sca:latest .
```

## Run

```
$ docker run -p 8080:8080 --env-file ./sca/env.sample sca:latest
```

----

## URLs Used

| URL                  | What it does                                                        |
| -------------------- | ------------------------------------------------------------------- |
| `/`                  | returns hostname of container                                       |
| `/health/`           | returns health status                                               |
| `/fail/`             | shutdown the container                                              |
| `/create-file/`      | creates file under junk_dir                                         |
| `/database-connect/` | connects to postgres database with the credentials in environments  |
| `/queue-connect/`    | connects to queue server with the credentials in environments       |
| `/cache-connect/`    | connects to redis cache server with the credentials in environments |
