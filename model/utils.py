from bs4.element import Tag

def is_error(container: Tag):
    # Check for error
    error_containers = container.findChildren(class_='error-container')
    if len(error_containers) > 0:
        error_code = error_containers[0].findChildren(class_='text-danger')[-1].text
        return error_code
    return False
