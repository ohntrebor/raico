import pytest
from scripts.helpers import is_large_file

# Função de teste para verificar o comportamento da função is_large_file.
def test_is_large_file():
    # Define um conteúdo pequeno com 4.999 caracteres (abaixo do limite).
    small_content = "a" * 4999

    # Define um conteúdo grande com 5.001 caracteres (acima do limite).
    large_content = "a" * 5001

    # Testa se a função retorna False para conteúdo pequeno.
    assert not is_large_file(small_content)

    # Testa se a função retorna True para conteúdo grande.
    assert is_large_file(large_content)
