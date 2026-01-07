import os
import shutil

from textnode import markdown_to_html_node


# source is either going to be a file or a directory. if it's a file, call shutils to move the file. if it's a directory, call the function on it again with a modified filepath for both the source and the destination.
def copy_filetree(source, destination, *, is_root=False):
    # Normalize to absolute paths once
    source_abs = os.path.abspath(source)
    dest_abs = os.path.abspath(destination)
    cwd = os.path.abspath(os.curdir)

    # Safety: Both must be inside cwd
    if not source_abs.startswith(cwd + os.sep):
        raise ValueError(f"source outside project: {source_abs}")
    if not dest_abs.startswith(cwd + os.sep):
        raise ValueError(f"source outside project: {dest_abs}")

    # Safety: destination must not *contain* source (would recurse into itself)
    if source_abs.startswith(dest_abs + os.sep):
        raise ValueError("destination may not be an ancestor of source")

    if os.path.isfile(source_abs):
        parent = os.path.dirname(dest_abs)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        shutil.copy(source_abs, dest_abs)
        return

    # Directory case
    if is_root:
        if os.path.exists(destination):
            shutil.rmtree(destination)
        os.mkdir(destination)
    else:
        if not os.path.exists(destination):
            os.mkdir(destination)

    for name in os.listdir(source):
        new_source = os.path.join(source, name)
        new_dest = os.path.join(destination, name)
        copy_filetree(new_source, new_dest)


def extract_title(markdown):
    block = markdown.lstrip().split("\n\n")[0]
    first = block.split(" ", maxsplit=1)[0].rstrip()
    text = block.split(" ", maxsplit=1)[1].strip()
    tag = f"h{len(first)}"
    if tag != "h1":
        raise Exception("first line should be heading, not subheading")
    return text


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        from_file = f.read()
        f.close()

    with open(template_path, "r") as f:
        template = f.read()
        f.close()

    html = markdown_to_html_node(from_file).to_html()
    title = extract_title(from_file)
    html = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    with open(dest_path, "w") as f:
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))

        f.write(html)
        f.close()


def main():
    # source = "static"
    # destination = "public"
    # copy_filetree(source, destination, is_root=True)
    from_path = "content/index.md"
    dest_path = "public/index.html"
    template_path = "template.html"
    generate_page(from_path, template_path, dest_path)


if __name__ == "__main__":
    main()
