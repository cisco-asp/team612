import yaml
from jinja2 import Template

def render_yaml_template(template_path, context):
    """
    Render a Jinja2 YAML template and return it as a Python dictionary.

    Args:
        template_path (str): Path to the Jinja2 YAML template file.
        context (dict): Dictionary of variables to substitute in the template.

    Returns:
        dict: Parsed YAML data as a Python dictionary.
    """
    with open(template_path, "r") as f:
        template = Template(f.read())
    
    rendered = template.render(context)
    return yaml.safe_load(rendered)

if __name__ == "__main__":
    context = {
        "xc_name": "TMO-21"
    }

    data = render_yaml_template("config.yml.j2", context)
    print(data)