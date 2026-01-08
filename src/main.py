import os
import shutil
import sys

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
    if dest_abs.startswith(source_abs + os.sep):
        raise ValueError("destination may not be inside source")

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


def generate_pages_recursive(
    from_path, template_path, dest_path, basepath, *, is_root=False
):
    abs_from_path = os.path.abspath(from_path)
    abs_dest_path = os.path.abspath(dest_path)
    abs_template_path = os.path.abspath(template_path)
    cwd = os.path.abspath(os.curdir)

    # Safety: Both must be inside cwd
    if not abs_from_path.startswith(cwd + os.sep):
        raise ValueError(f"source outside project: {abs_from_path}")
    if not abs_dest_path.startswith(cwd + os.sep):
        raise ValueError(f"source outside project: {abs_dest_path}")

    # Safety: destination must not *contain* source (would recurse into itself)
    if abs_from_path.startswith(abs_dest_path + os.sep):
        raise ValueError("destination may not be an ancestor of source")
    if abs_dest_path.startswith(abs_from_path + os.sep):
        raise ValueError("destination may not be inside source")

    if os.path.isfile(abs_from_path):
        parent = os.path.dirname(abs_dest_path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        dest_root, dest_ext = os.path.splitext(abs_dest_path)
        if dest_ext == ".md":
            abs_dest_path = dest_root + ".html"
        generate_page(abs_from_path, abs_template_path, abs_dest_path, basepath)
        return

    if is_root:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        os.mkdir(dest_path)
    else:
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)

    for name in os.listdir(from_path):
        new_from_path = os.path.join(from_path, name)
        new_dest_path = os.path.join(dest_path, name)
        generate_pages_recursive(
            new_from_path, abs_template_path, new_dest_path, basepath
        )


def generate_page(from_path, template_path, dest_path, basepath):
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
    html = html.replace('href="/', f'href="/{basepath}').replace(
        'src="/', f'src="/{basepath}'
    )

    with open(dest_path, "w") as f:
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))

        f.write(html)
        f.close()


def main(argv):
    basepath = sys.argv[1] if len(argv) > 0 else "/"
    print(basepath)
    source = "static"
    destination = "docs"
    copy_filetree(source, destination, is_root=True)
    from_path = "content"
    dest_path = "docs"
    template_path = "template.html"
    generate_pages_recursive(from_path, template_path, dest_path, basepath)


if __name__ == "__main__":
    main(sys.argv[1:])
