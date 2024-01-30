# Parts Warehouse RestAPI

## Introduction

Welcome to the Parts Warehouse RestAPI project! This project is designed to manage warehouse, featuring a MongoDB database and CRUD functionality for 'parts' and 'categories' collections, as well as a specific search endpoint for parts.

## Why FastAPI?

FastAPI was the go-to choice for its great suitability for REST APIs, pleasant official documentation of the fastAPI itself, flexibility, and speed. It allows quick development, automatic Swagger documentation, and can handle asynchronous tasks really well — all key for a top-notch API.
## Setup & Installation

1. Clone the repository. 
    You can do this by running:
    ```bash 
    git clone [URL_of_Your_Git_Repository]
2. Make .env file. Example file to help you set it correctly is in the project and it is called '.env.example'. It's main purpose is to set details regarding database. 
3. Make sure Docker is installed on your machine. If it's not installed, you can download and install it from Docker's official website.
4. Run the application container:
- Navigate to the Project Directory
   ```bash  
  cd [Path_to_Project_Directory]
- Build the Application Container
   ```bash
   docker build -t parts-warehouse-api .
- After the build is complete, run the container with:
   ```bash
   docker run -d -p 8080:8080 parts-warehouse-api
5. With the application running, you can access the API at http://localhost:8080 or the Swagger documentation at http://localhost:8080/docs.


## Database Structure

In this project, I am utilizing MongoDB, a non-relational (NoSQL) database, known for its flexibility and scalability. Unlike traditional relational databases, MongoDB stores data in documents, which allows for a more dynamic and adaptable schema design. 

Our MongoDB database is structured into two separate collections: parts and categories. 
### Parts Collection

- This collection stores individual parts available in the warehouse.
- Each document in the parts collection represents a unique part, containing details such as serial number, name, description, category, quantity, price, and location.
- The structure is designed to efficiently store and retrieve information about each part, streamlining the inventory management process.

### Categories Collection
- The categories collection organizes parts into a hierarchical structure.
- Each category document includes a name and an optional parent_name.
- The parent_name field loosely connects one category to another, forming a category tree. This allows for a flexible and intuitive categorization of parts, which can be especially useful for organizing a wide range of items.
- This loose coupling via the parent_name field enables easy updates and modifications to the category structure without impacting the integrity of the overall database.


- `name`: String - Name of the category.
- `parent_name`: String - Name of the parent category. If empty, indicates a base category.


### Parts Collection Endpoints
_I recommend using **swagger** that can be accessed on `/docs`, in case of local dev it will be `localhost:8080/docs`_ 

#### `POST /parts/`
- **Description**: Add a new part to the warehouse.
- **Conditions**: 
  - Checks if a part with the same serial number already exists. If so, it prevents duplication.
  - Validates that the part is not assigned to a base category.

#### `PUT /parts/{serial_number}`
- **Description**: Update an existing part identified by its serial number.
- **Conditions**: 
  - Ensures the part exists before attempting an update.
  - Allows updating partial fields.
  - Validates updated category information.

#### `GET /parts/{serial_number}`
- **Description**: Retrieve detailed information about a specific part using its serial number.

#### `GET /parts/`
- **Description**: List all parts in the warehouse.

#### `DELETE /parts/{serial_number}`
- **Description**: Delete a specific part from the warehouse.
- **Conditions**: 
  - Checks if the part exists before deletion.

#### `GET /parts/search/`
- **Description**: Search for parts based on various fields such as name, description, category, etc.

### Categories Collection Endpoints

#### `POST /categories/`
- **Description**: Add a new category.
- **Conditions**: 
  - Prevents creation of a category with a duplicate name.
  - Sets the category as base category if there is no parent category.

#### `PUT /categories/{category}`
- **Description**: Update an existing category.
- **Conditions**: 
  - Ensures the category exists before updating.
  - Updates child categories if the parent category name changes.
  - Verifies if the category can be changed to a base category based on its association with parts.

#### `GET /categories/{category}`
- **Description**: Retrieve details of a specific category.

#### `GET /categories/`
- **Description**: List all categories in the warehouse.

#### `DELETE /categories/{category}`
- **Description**: Delete a specific category.
- **Conditions**: 
  - Ensures there are no parts directly associated with the category before deletion.
  - Verifies that no child categories with associated parts exist before deletion.
  - If the deleted category is a parent, updates the 'parent_name' of its child categories.
  - If the deleted parent category was a base category, its child categories become base categories.
