IP Scanner
IP Scanner is a simple, web-based tool for scanning and managing network IP addresses. It's designed to provide a quick and easy way to see which hosts are active on your network.

#### Key Features
- **Web-based Interface:** Access and manage your scans from any web browser.

- **CIDR Management:** Easily add, edit, or remove CIDR networks for scanning.

- **Live Scanning:** Click on a network to initiate a scan and view the list of "alive" IP addresses.

#### Deploying IP Scanner with Docker
The easiest way to run this application is by using Docker. Follow the steps below to get your IP Scanner instance up and running.

**1. Pull the Docker Image**
First, you'll need to pull the Docker image from the public registry.

```shell
docker pull chan3845/ip-scanner:v1.0.0
```

**2. Configure Persistent Storage**
For your CIDR networks to be saved permanently, you need to use a persistent volume. This involves creating a cidrs.json file on your local machine and mounting it into the container.

Create an empty cidrs.json file in a location of your choice. For example, you can create it in your home directory within a new folder:

```shell
mkdir -p $HOME/ip_scanner
cd $HOME/ip_scanner
vi cidrs.json
```

The cidrs.json file should contain IP lists array to start:
```shell
[
  "172.20.201.0/24",
  "192.168.201.0/24"
]
```

Or you can use the following to start with an empty list.
```shell
[]
```


**3. Run the Container**
Now you can run the container the docker run command. 

```shell
docker run -d -p 5000:5000 -v $HOME/ip_scanner/cidrs.json:/app/cidrs.json -v /etc/localtime:/etc/localtime:ro chan3845/ip-scanner:v1.0.0
```


**4. Access the Application**
Once the container is running, you can access the IP Scanner application by navigating to your browser.

If you are running Docker on your local machine, visit: http://localhost:5000

<img width="1868" height="998" alt="image" src="https://github.com/user-attachments/assets/e38b96c9-b627-420c-9780-eb9aebf2c63b" />
