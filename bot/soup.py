def delete_soup_nodes(soup, node_name):
    node = soup.find(node_name)
    while node is not None:
        node.decompose()
        node = soup.find(node_name)
