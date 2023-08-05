# MONGO CLI


> A CLI tool for making MongoDB management 10x easier
<br />

MongoDB Command Line Interface (CLI), a utility designed for developers, enabling easy interaction with your MongoDB databases via a terminal-based interface. Utilize straightforward commands to effortlessly execute advanced MongoDB operations on your existing documents, collections, and databases.

Elevate your database management process with the streamlined efficiency of mongo-cli, simplifying the way you navigate, query, and control your MongoDB ecosystem.

<br/>

## ⚙️ REQUIREMENTS

>  **IMPORTANT** 
> This tool requires `MongoDB` and `Python` preinstalled in your system to get started with it.

### If Not Yet Installed 

   - You can install Python from [here](https://www.python.org/downloads/)
   - You can install MongoDB from [here](https://www.mongodb.com/docs/manual/installation/)

Install and setup requirements for error free usage

<br/>

## 🚀 GETTING STARTED

Run the given command on you terminal to use mongo-cli :

1) `git clone https://github.com/PROBLEMATIC-CODER/mongo-cli.git` on your git terminal.

2) `pip install` for installing required packages. 

3) `cd path/to/project` access the folder in terminal

4) `python.exe main.py` in the project root directory to start using.
 
5)  `Giving ⭐️ to repository` helping me to to make such kind of tools for our community

</br>

## 💡 START USING

> **NOTE**
> To start using the mongo-cli you first have to enter the `port` on which your MongoDB is running. 

After being successfull connected to your MongoDB server you will be ready to go and see the interface like given below.

</br>

![Starting Image](https://github.com/PROBLEMATIC-CODER/images/blob/master/Mongo%20CLI/mongo_cli.png?raw=true)

</br>

To see all available commands available for performing operations, you can use command `show commands`

</br>

<div align="center">

# **❤️❤️ Show Some Love By Giving A Heart ❤️❤️** 

</div>

<br/>

##  🛠️ BASIC COMMANDS

   Feel free to change content or customize commands according to your requirements.

   To get started with this tool you need to know some basic commands to control this CLI tool.

   > **NOTE** 
   > Use `show commands` to see all available useful commands in cli
   

1) **Check Mongo Status:**

    To get current working status of MongoDB you can use -

    ```console
    show status
    ```
2) **Go Back And Next:**

    Going back and moving forward essentially involves navigating between recent steps you've taken. For instance, if you initially *entered a database* and then 
    proceeded to *enter a collection*, using the back from the *collection stage* will return you to the *database stage* and using next from the *database stage* 
    will return you to *collection stage* .

    For going back you can use
    ```console
    back
    ```

    for going forward you can use
    ```console
    next
    ```
    
4) **Going Back To Start:**

   ```console
   home
   ```

5) **Managing MongoDB Service:**

   > **IMPORTANT**
   >  Managing MongoDB service requires **admin permission** and only supported in **Windows** operating system

   To start MongoDB service you can use -
   
    ```console
    start mongo
    ```

   In order to stop MongoDB service you can use -
   
    ```console   
    stop mongo
    ```

   For restarting MongoDB service you can use -
   
    ```console
    restart mongo
    ```
   
6) **Getting information about MongoDB on system**
   
   ```console
   get info
   ```
8) **Getting recent logs**

   ```console
   logs <log count>
   ```
   Don't forget to replace `<log count>` with count of *recent logs* you want to see

9) **RESTARTING CLI**
   ```console
    restart
   ```
<br/>


## 🔚 CONCLUSION

This tool is your partner in effortlessly managing and performing operations on your MongoDB databases. It's here to simplify your database tasks and make your life easier.

With user-friendly commands, you can navigate through databases, collections, and documents seamlessly. From basic tasks to more advanced operations, you can perform with this CLI.

Thank you for choosing our MongoDB CLI. If you have any questions or suggestions, I am here to help. Happy MongoDB management!
