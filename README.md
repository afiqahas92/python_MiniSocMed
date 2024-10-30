## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Docker](https://www.docker.com/get-started)

## Getting Started

Follow these steps to get a copy of the project up and running on your local machine.

### Pull the Docker Image

To get the Docker container, run the following command in your terminal:

```bash
docker pull afiqahas92/arba-travel:latest
````
Run the Docker Container
Once the image is pulled, you can run the Docker container with the following command:

bash
Copy code
```
docker run -d -p 5000:5000 afiqahas92/arba-travel
