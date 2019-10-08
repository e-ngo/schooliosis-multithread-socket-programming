# CSC645-01 Computer Networks: Template for your web proxy server assingnment
This is an optional template for assignment #2 Web Proxy Server. The template is a complete Python/Flask project with
all the most important signature methods for this project. The most important ones contain an algorithmic description
to be followed when implemented. This template also contains all the neccesary HTML files for this project. However, 
you are free to use your own templates for this assignment. Note: page asking username and password is not included in 
this template

## Add project to your private class repository
1. Clone or download this project in your local machine 
2. Create a local git repository for this project
3. Add a new remote repository. This remote repository should be your class private repository 
and the project should be hosted in ~/applications/web-server-proxy/ 

## Open project with PyCharm (optional). You can use any IDE supporting Python/Flask 
1. Open PyCharm
2. Select check project from version control option.
3. Select git
4. Add the following URL: https://github.com/sfsu-joseo/cac645-01-template-web-proxy-server-project.git 
5. If everything works as expected, you are ready to go

## First run. 
This will be explained in class in detail. But in case you miss it:
1. Run web-proxy-server.py file
2. If no error, the PyCharm console will start the localhost server and will provide you a url in console. 
3. Click or copy and paste that URL into your prefered browser, and it will load the hone page of this assignment
4. I created for you a simple textbox that emulates a browser. 
5. In order to access the proxy-settings enter the following url in the textbox provided in the home page: http://127.0.0.1:5000/proxy-settings. 
Note that your port may be different depending on the PyCharm configuration. 
6. If no error, you'll see a basic template for the proxy settings page

## Project content
First of all, you can change the server and client files by your own ones from assignment #1 as long as they are implemented correctly.
Secondly, This project has everything you need to create a good proxy server with cache. I provided signatured methods for all the
most imoortant functionalities including algorithmic details for some of them, Please, take your time to explore all 
the parts of this template project. Some methods are already implemented, but they still depend on other methods that are not yet imolemented.
Also note that methods starting with underscore are private methods. Also note that I set all the methods to return 0. You need
to remove that return as needed when you implement them. Some methods are also VOID ones

