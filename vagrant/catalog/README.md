# Catalog App

Catalog App is a web application that provide a list of items within a veriety of categories and integrate user registration and authentication with Google plus. Authenticated users should have the ability to post, edit, and delete their own items and categories.

# Quick start

1. Install Vagrant and VirtualBox if you don't have.

2. From the terminal, run:
    git clone https://github.com/halee9/fullstack-nanodegree-vm
    There is a catalog folder that include all files for catalog app.

3. Launch the Vagrant VM (by typing **vagrant up** in the directory fullstack-nanodegree-vm/vagrant from the terminal).

4. Once VM is up and running, type **vagrant ssh**.

5. Move to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

6. Now type **python catalog_db.py** to initialize the database.

7. Type **python catalog_data* to populate the database with categories and items. (Optional)
    **Note:** There are 2 categories and 4 items, but you can't modify and delete this categories and items because this items were created by another user.

8. Create client ID and client secret
    a. In your browser, visit http://console.developers.google.com
    b. Log in and click the **Create Project** button.
    c. Type **Catalog All** in the project name. Google automatically creates a project ID for you. And create project.
    d. Click **APIs and auth** on the left-hand menu, then select **Credentials**.
    e. In the OAuth 2.0 section go ahead and click **Create new Client ID**. Make sure Web application is selected and then click **Configure consent screen**. Put catalog app in the **product name shown to users**. And **save**.
    f. Then **click Create Client ID**. Now that we see that our web application has a client ID complete with email address, client secret, redirect URIs, and JavaScript origins. Now let's go ahead and click **Edit Settings**.
    g. In the **authorized JavaScript origins**, add http://localhost:5000. And in the **Authorized redirect URIs**, add http://localhost:5000/login and http://localhost:5000/gconnect. and click **Update"
    h. Click **Download JSON** button, save downloaded file in your **catalog** folder on your local computer.
    i. Open **login.html** from templates folder, and find line 10 **data-clientid** and set your own **client ID** as the value.

8. Type **python app.py** to run the Flask web server. In your browser visit **http://localhost:5000** to view the catalog app. You should be able to view, add, edit, and delete items and catagories.


