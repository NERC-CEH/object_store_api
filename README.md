# Object Store API 

[Read the docs!](https://nerc-ceh.github.io/object_store_api)

This repository contains a web API designed to make it easier to interact with, and build applications on, research data held in an s3 object store.

It was originally part of the [AMI system](https://github.com/AMI-system) for collecting and classifying images of moths from field cameras, and is intended for use in other projects that have a small to medium sized collection of images or sound samples and want to automate more of their data flow.

The install and setup documentation comes from the useful [NERC-CEH python project template](https://github.com/NERC-CEH/python-template)


## Getting Started

### Using the Githook

From the root directory of the repo, run:

```
git config --local core.hooksPath .githooks/
```

This will set this repo up to use the git hooks in the `.githooks/` directory. The hook runs `ruff format --check` and `ruff check` to prevent commits that are not formatted correctly or have errors. The hook intentionally does not alter the files, but informs the user which command to run.

### Installing the package

Install the code with only the dependencies needed to run it:

```
pip install .
```

To work on the docs:

```
pip install -e .[docs]
```

To work on tests:

```
pip install -e .[test]
```

To run the linter and githook:

```
pip install -e .[lint]
```

The docs, tests, and linter packages can be installed together with:

```
pip install -e .[dev]
```

### Documentation 

```
cd docs
make apidoc
```

To keep your documentation in sync with the package name. You may need to delete a file called `os_api.rst` from `./docs/sources/...`

If you want docs to be published to github pages automatically, go to your repo settings and enable docs from GitHub Actions and the workflows will do the rest.

### Building Docs Locally

The documentation is driven by [Sphinx](https://www.sphinx-doc.org/) an industry standard for documentation with a healthy userbase and lots of add-ons. It uses `sphinx-apidoc` to generate API documentation for the codebase from Python docstrings.

To run `sphinx-apidoc` run:

```
# Install your package with optional dependencies for docs
pip install -e .[docs]

cd docs
make apidoc
```

This will populate `./docs/sources/...` with `*.rst` files for each Python module, which may be included into the documentation.

Documentation can then be built locally by running `make html`

### Run the Tests

To run the tests run:

```
#Install package with optional dependencies for testing
pip install -e .[test]

pytest
```

## Run the API 

This needs a set of credentials - an Access Key, a Secret Key and an Endpoint.

[Overview of obtaining these details from JASMIN](https://github.com/NERC-CEH/object_store_tutorial/?tab=readme-ov-file#an-introduction-to-object-storage)

`.env` contains variables which hold the key-value pairs, they are automatically loaded when you run the API. The key names all include `AWS` because they come originally from libraries to work with Amazon s3 storage, but JASMIN supports the same de facto standard.

Contents of `.env`:

```
AWS_ACCESS_KEY_ID="key goes here"
AWS_SECRET_ACCESS_KEY="secret goes here"
AWS_URL_ENDPOINT="url goes here"
```

### Standalone, for testing

`python src/os_api/api.py`

This will bring up the OpenAPI documentation on localhost:8080

### With `uvicorn` using the `fastapi` cli 

`fastapi run --workers 4 src/os_api/api.py`

### In a container

#### docker

```
docker build -t os_api .
docker run -f -p 80:80 os_api
```

#### podman

```
podman build -t os_api .
podman run --env-file=.env -p=8000 --expose=8000 os_api
```

### Automatic Versioning

This codebase is set up using [autosemver](https://autosemver.readthedocs.io/en/latest/usage.html#) a tool that uses git commit history to calculate the package version. Each time you make a commit, it increments the patch version by 1. You can increment by:

* Normal commit. Use for bugfixes and small updates
    * Increments patch version: `x.x.5 -> x.x.6`
* Commit starts with `* NEW:`. Use for new features
    * Increments minor version `x.1.x -> x.2.x`
* Commit starts with `* INCOMPATIBLE:`. Use for API breaking changes
    * Increments major version `2.x.x -> 3.x.x`

### Docker and the ECR

The python code can be packaged into a docker image and pushed to the AWS ECR. For the deployment to succeed you must:

* Add 2 secrets to the GitHub Actions:
    * AWS_REGION: \<our-region\>
    * AWS_ROLE_ARN: \<the-IAM-role-used-to-deploy\>
* Add a repository to the ECR with the same name as the GitHub repo
 
