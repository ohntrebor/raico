def is_large_file(content):
    """Verifica se o arquivo é muito grande para análise."""
    return len(content) > 5000
