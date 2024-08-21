"""
FastAPI for uploading images to an S3 server.
"""

import asyncio
import logging
import os
from time import perf_counter

import aioboto3
import boto3
import uvicorn
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# Configure logging
logging.basicConfig(
    filename="upload_logs.log",  # Log file path on the server
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

tags_metadata = [
    {
        "name": "Data",
        "description": "Operations for data management in the server, uploading and downloading.",
    },
    {"name": "Other", "description": "Other operations."},
]

app = FastAPI()

# Set up CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load AWS credentials and S3 bucket name from .env file
# Rather than depend on the presence of credentials.json in the package
load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_URL_ENDPOINT = os.environ.get("AWS_URL_ENDPOINT", "")

CONCURRENCY_LIMIT = 200  # Adjust this value based on your server capabilities


# Wrapped in function to use as dependency_override
def boto_session() -> aioboto3.Session:
    return aioboto3.Session()


session = boto_session()


@app.get("/", include_in_schema=False)
async def main() -> RedirectResponse:
    "Redirect main root url to the documentation."
    return RedirectResponse(url="/docs")


@app.post("/create-bucket/", tags=["Data"])
async def create_bucket(bucket_name: str = Query("", description="")) -> JSONResponse:
    "Endpoint to create a new bucket in the server."
    async with session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_URL_ENDPOINT,
    ) as s3_client:
        try:
            await s3_client.create_bucket(Bucket=bucket_name)
            return JSONResponse(
                status_code=200,
                content={"message": f"Bucket '{bucket_name}' created successfully"},
            )
        except s3_client.exceptions.BucketAlreadyExists:
            return JSONResponse(
                status_code=409, content={f"Bucket {bucket_name} already exists."}
            )
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            return JSONResponse(
                status_code=409,
                content={f"Bucket {bucket_name} is already owned by you."},
            )
        except Exception as e:
            return JSONResponse(
                status_code=500, content={f"Error creating bucket: {str(e)}"}
            )


@app.post("/generate-presigned-url/", tags=["Data"])
async def generate_presigned_url(
    filename: str = Form(...),
    file_type: str = Form(...),
) -> JSONResponse:
    "Endpoint to generate a unique presigned url for uploading files."
    bucket_name = ""
    key = filename

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_URL_ENDPOINT,
    )
    try:
        # Generate a presigned URL for the S3
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": key, "ContentType": file_type},
            ExpiresIn=3600,
        )  # URL expires in 1 hour

        return JSONResponse(status_code=200, content=presigned_url)
    except NoCredentialsError:
        return JSONResponse(
            status_code=403, content={"error": "No AWS credentials found"}
        )
    except PartialCredentialsError:
        return JSONResponse(
            status_code=403, content={"error": "Incomplete AWS credentials"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/upload/", tags=["Data"])
async def upload(
    files: list[UploadFile] = File(...),
) -> JSONResponse:
    "Endpoint to upload a list of files to the server."
    start_time = perf_counter()
    s3_bucket_name = ""
    key = ""

    try:
        tasks = [upload_file(s3_bucket_name, key, file) for file in files]
        await asyncio.gather(*tasks)
    except Exception as e:
        print("Error:", e)
        return JSONResponse(status_code=500, content={str(e)})

    end_time = perf_counter()
    print(f"{end_time - start_time} seconds.")

    logger.info("Uploaded %i", len(files))

    return JSONResponse(
        status_code=200,
        content={"message": "All files uploaded and verified successfully"},
    )


async def upload_file(s3_bucket_name: str, key: str, file: UploadFile) -> None:
    "Endpoint to upload a single file to the server."
    async with session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_URL_ENDPOINT,
    ) as s3_client:
        try:
            # Upload updated file to S3
            await s3_client.upload_fileobj(
                file.file, s3_bucket_name, f"{key}/{file.filename}"
            )
            # print(f"File {key}/{file.filename} uploaded successfully.")
        except Exception as e:
            logger.error(
                "Error when uploading %s to %s/%s.", file.filename, s3_bucket_name, key
            )
            return JSONResponse(
                status_code=500,
                content={"message": f"Error uploading {key}/{file.filename}: {e}"},
            )


@app.post("/check-file-exist/", tags=["Data"])
async def check_file_exist(filename: str = Form(...)) -> JSONResponse:
    "Endpoint to check if file already exists in the server."
    bucket_name = ""
    key = filename

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_URL_ENDPOINT,
    )

    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        message = {"exists": True}  # File exists
        return JSONResponse(status_code=200, content=message)
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            message = {"exists": False}  # File doesn't exist
            return JSONResponse(status_code=200, content=message)
        return JSONResponse(status_code=500, content={"message": f"{e}"})
    except NoCredentialsError:
        return JSONResponse(
            status_code=403, content={"message": "No AWS credentials found"}
        )
    except PartialCredentialsError:
        return JSONResponse(
            status_code=403, content={"message": "Incomplete AWS credentials"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"{e}"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
