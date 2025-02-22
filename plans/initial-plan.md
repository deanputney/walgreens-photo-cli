# Initial Plan for Walgreens Photo Printing CLI

This document outlines a detailed, iterative development plan for the Walgreens Photo Printing CLI tool. The plan is based on the specifications in `specs/initial-spec.md` and is intended to be used as a series of prompts for a code-generation LLM. Each prompt builds incrementally from the previous work, ensuring no orphaned or hanging code.

---

## Step-by-Step Blueprint Overview

1. **Project Setup & CLI Skeleton**

   - **Objective:** Set up the base project structure and implement basic CLI functionality.
   - **Tasks:**
     - Create a main entry point.
     - Parse command line arguments.
     - Provide help (`-h`/`--help`) and version (`-v`/`--version`) outputs.
     - Accept a single positional argument: a path to an image file or folder.

2. **Configuration Management**

   - **Objective:** Manage user credentials through a configuration file.
   - **Tasks:**
     - Identify the config file location at `~/.config/walgreens-print/config.yaml`.
     - If the config file is missing:
       - Create the configuration directory.
       - Prompt the user for API key, Affiliate ID, and Store ID.
       - Write these credentials to a YAML file.
     - On subsequent runs, load and validate the configuration file:
       - Check for valid YAML.
       - Ensure that all required fields (`api_key`, `affiliate_id`, `store_id`) are present and non-empty.
       - Output clear error messages on failure.

3. **Image Validation Module**

   - **Objective:** Validate image inputs for both single file and folder inputs.
   - **Tasks:**
     - Determine if the input is a file or a folder.
     - For a folder, collect all JPG/PNG images and ensure no more than 100 photos are included; otherwise, exit with an error.
     - For each image file:
       - Check that the file exists.
       - Confirm that the file extension is `.jpg`, `.jpeg`, or `.png`.
       - Optionally perform a check to verify that the file is a readable image.
       - Validate the file name for allowed characters (letters, numbers, dashes, and underscores).

4. **API Integration Module**

   - **Objective:** Handle communication with the Walgreens API.
   - **Tasks:**
     - Simulate or implement API calls to submit image(s) for printing.
     - Prepare the request payload based on validated images.
     - Integrate robust error handling:
       - Catch network errors (connection issues, timeouts).
       - Handle API errors (invalid credentials, API downtime).
       - In partial failures, complete the order with the valid uploads, report failed images, and display order details.
     - Display a success message with order details upon successful submission.

5. **Cleanup and Error Handling**

   - **Objective:** Ensure a clean runtime environment and clear error reporting.
   - **Tasks:**
     - Remove any temporary files created during execution.
     - Ensure cleanup is performed even if an error occurs.
     - Integrate consistent error handling across the application, with clear, user-friendly error messages.

6. **Final Integration and Testing**
   - **Objective:** Wire all modules together into a cohesive tool.
   - **Tasks:**
     - Ensure the main function integrates CLI, config management, image validation, API integration, and cleanup.
     - Test the full workflow with various inputs (valid, missing config, invalid images, API failures).
     - Document a testing strategy for both unit tests and end-to-end integration tests.

---

## Iterative Development Breakdown & Prompts

Below is a series of prompts to be used with a code-generation LLM. Each prompt is tagged using a text code block with clear instructions.

---

### **Prompt 1: Initial CLI Skeleton Setup**

```text
Create a basic CLI application for the Walgreens Photo Printing tool. The application should:
Parse command line arguments.
Provide help text when run with '-h' or '--help', or when no arguments are provided.
Accept a single positional argument for the image file or folder path.
Provide a version option (e.g., '-v' or '--version') that outputs "walgreens-print version 1.0.0".
Focus only on the argument parsing and basic CLI setup, using best practices and an appropriate library (e.g., argparse in Python). The main function should act as the entry point.
```

---

### **Prompt 2: Configuration Management Module**

```text
Develop a configuration management module that:
- Determines the config file location at '~/.config/walgreens-print/config.yaml'.
- On the first run (when the config file does not exist), creates the config directory, and prompts the user for:
  - API key
  - Affiliate ID
  - Store ID
- Saves these credentials in YAML format.
- On subsequent runs, reads and validates the config file, ensuring:
  - The file is valid YAML.
  - Required fields ('api_key', 'affiliate_id', 'store_id') exist and are non-empty.
- Provides clear error messages if validation fails (e.g., "Error: Missing required field 'api_key' in config file").
Ensure this module is importable and callable from the main application.
```

---

### **Prompt 3: Image Validation Module**

```text
Create an image validation module that handles:
- Accepting an input path which can be either a single image file or a directory.
- If the input is a directory, collect all image files (JPG and PNG) and enforce a maximum limit of 100 images. If the limit is exceeded, return an appropriate error.
- For every image file, perform the following validations:
  - Check that the file exists.
  - Check that the file has a valid extension: '.jpg', '.jpeg', or '.png'.
  - (Optional) Validate that the file is a readable image using simple heuristics or an image processing library.
  - Check that file names contain only allowed characters (letters, numbers, dashes, underscores).
- Return a list of validated image file paths, or a detailed error message for any invalid images.
Ensure the module is designed to be small, testable, and integrable into the main workflow.
```

---

### **Prompt 4: API Integration Module**

```text
Build an API integration module that:
- Prepares the request payload and simulates sending print orders to the Walgreens API.
- Incorporates error handling to manage:
  - Network errors (e.g., connection timeouts, no internet connection).
  - API errors (e.g., invalid credentials, API unavailability), including displaying the error messages returned from the API.
- For scenarios where only a subset of images successfully upload (partial failures):
  - Complete the order for the successful images.
  - Report the images that failed.
  - Display the order confirmation, including order number and pickup details.
Ensure the module exposes a clear interface for submitting images and receiving a response. Focus on clear API interfaces and robust error handling.
```

---

### **Prompt 5: Cleanup and Global Error Handling**

```text
Enhance the application by adding cleanup functionality that:
- Ensures any temporary files created during the upload/processing phase are removed, whether the process succeeds or fails.
- Catches and logs errors from configuration management, image validation, or API integration.
- Gracefully terminates the program with relevant error messages if an error occurs.
- Integrates the cleanup process into the main execution flow so that no temporary data remains after the run.
This prompt should ensure that error handling and cleanup are correctly wired in the overall application.
```

---

### **Prompt 6: Final Integration and Wiring Everything Together**

```text
Wire together all the previously developed modules into the main application:
- Start with parsing command line arguments.
- Load and validate the configuration.
- Validate the input (either a single image file or folder of images).
- Call the API integration module to submit the order.
- Handle both success and failure cases, displaying comprehensive messages (e.g., success confirmation with order details).
- Ensure that cleanup operations run regardless of whether the submission is successful or if any errors occur.
This final integration should demonstrate a complete, end-to-end working application without any orphaned or unconnected functionality.
```

---

### **Prompt 7: Testing and Final Review**

```text
Develop a testing strategy and include instructions for testing the Walgreens Photo Printing CLI:
- Write unit tests for individual modules: CLI parsing, configuration management, image validation, and API integration.
- Develop integration tests that simulate the entire workflow, including:
  - Valid input scenarios.
  - Cases with missing configuration.
  - Folder input exceeding 100 images.
  - API failures or network issues.
- Document manual testing steps for verifying:
  - Error message clarity.
  - Cleanup of temporary files.
  - Correct handling of partial image upload failures.
- Provide guidance on how to execute these tests as part of the development process.
The testing strategy must validate that every component of the tool works cohesively according to the specifications.
```

---

## Conclusion

This plan provides a structured, incremental roadmap for building the Walgreens Photo Printing CLI tool. Each step is designed to be small enough to implement and test independently while ensuring overall progress and integration. Follow these prompts sequentially for a seamless development process ensuring adherence to all specified requirements.
