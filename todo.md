# Todo Checklist for Walgreens Photo Printing CLI

This checklist outlines all the tasks needed to complete the Walgreens Photo Printing CLI tool. Check off each task upon completion to ensure all requirements are met.

---

## 1. Project Setup & CLI Skeleton

- [ ] **Create Main Entry Point**
  - [ ] Create the main file (e.g., `main.py`) as the application entry point.
- [ ] **Command Line Argument Parsing**
  - [ ] Use a library (e.g., `argparse`) to parse CLI arguments.
  - [ ] Accept a single positional argument for the image file or folder.
- [ ] **Help & Version Options**
  - [ ] Implement help text (`-h`/`--help`) that displays usage instructions.
  - [ ] Implement version option (`-v`/`--version`) that outputs `"walgreens-print version 1.0.0"`.

---

## 2. Configuration Management

- [ ] **Determine Config File Location**
  - [ ] Set the config file location to `~/.config/walgreens-print/config.yaml`.
- [ ] **Handle Missing Config**
  - [ ] Create the configuration directory if it does not exist.
  - [ ] Prompt the user for:
    - [ ] API key
    - [ ] Affiliate ID
    - [ ] Store ID
  - [ ] Save these credentials in YAML format.
- [ ] **Load and Validate Config**
  - [ ] Read the config file on subsequent runs.
  - [ ] Validate that the file is valid YAML.
  - [ ] Ensure required fields (`api_key`, `affiliate_id`, `store_id`) exist.
  - [ ] Check that none of the fields are empty.
  - [ ] Display clear error messages if validation fails.

---

## 3. Image Validation Module

- [ ] **Input Path Handling**
  - [ ] Accept an input path that can be either a single image file or a directory.
- [ ] **Directory Handling**
  - [ ] If the input path is a directory, collect all image files (JPG/PNG).
  - [ ] Enforce a maximum limit of 100 images.
  - [ ] Report an error if more than 100 images are present.
- [ ] **File Validations**
  - [ ] Verify that each image file exists.
  - [ ] Ensure the file extension is one of: `.jpg`, `.jpeg`, or `.png`.
  - [ ] Optionally, validate that the file is a readable image (using simple heuristics or an image library).
  - [ ] Check that file names contain only allowed characters (letters, numbers, dashes, and underscores).
- [ ] **Output**
  - [ ] Return a list of validated image file paths.
  - [ ] Provide detailed error messages for any invalid images.

---

## 4. API Integration Module

- [ ] **Prepare API Payload**
  - [ ] Create a module that builds the request payload using validated images.
- [ ] **Simulate/Implement API Call**
  - [ ] Simulate sending the print order request to the Walgreens API.
- [ ] **Error Handling**
  - [ ] Handle network errors (e.g., timeouts, connection failures).
  - [ ] Handle API errors (e.g., invalid credentials, service unavailability) and display their messages.
  - [ ] In cases of partial image upload failures:
    - [ ] Process the successfully uploaded images.
    - [ ] Report which images failed to upload.
    - [ ] Display order confirmation details (order number and pickup information).

---

## 5. Cleanup and Global Error Handling

- [ ] **Temporary Files Cleanup**
  - [ ] Remove any temporary files created during processing.
  - [ ] Ensure cleanup routines run even if an error occurs.
- [ ] **Global Error Handling**
  - [ ] Catch and log errors from configuration management, image validation, and API integration.
  - [ ] Gracefully terminate the program with clear error messages.

---

## 6. Final Integration

- [ ] **Module Integration**
  - [ ] Wire together CLI parsing, configuration management, image validation, API integration, and cleanup in the main execution flow.
- [ ] **Workflow Execution**
  - [ ] Validate input (single image or folder).
  - [ ] Load and validate the configuration.
  - [ ] Submit the print order with the API integration module.
  - [ ] Ensure all success and error messages are comprehensive.
  - [ ] Guarantee that cleanup operations run regardless of the outcome.

---

## 7. Testing & Final Review

- [ ] **Unit Testing**
  - [ ] Write unit tests for CLI parsing.
  - [ ] Write unit tests for configuration management.
  - [ ] Write unit tests for image validation.
  - [ ] Write unit tests for the API integration module.
- [ ] **Integration Testing**
  - [ ] Develop integration tests to simulate the full workflow:
    - [ ] Valid input scenarios.
    - [ ] Scenarios with missing configuration.
    - [ ] Directory input exceeding 100 images.
    - [ ] API and network failure scenarios.
- [ ] **Manual Testing**
  - [ ] Document manual testing steps to verify:
    - [ ] Clear and user-friendly error messages.
    - [ ] Successful cleanup of temporary files.
    - [ ] Proper handling of partial image upload failures.
- [ ] **Code Review & Refactoring**
  - [ ] Conduct a thorough code review.
  - [ ] Refactor any orphaned or unintegrated code.
  - [ ] Ensure code follows best practices and is maintainable.

---

## Additional Notes

- Ensure that every module is testable and importable.
- Follow the iterative prompts from the initial plan to avoid large jumps in complexity.
- Maintain comprehensive documentation for future reference.

Happy Coding!
