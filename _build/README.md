# Build do site

O site publicado é o conjunto de arquivos `.html` e `assets/` na raiz do repositório.

- `source/`: páginas editáveis (formato do editor de design do Claude).
- `export.py`: gera os `.html` da raiz a partir de `source/`, copia os assets usados para `assets/` e remove os que não são mais usados.
- `gx.js`: comportamento da galeria dos cases (passa sozinha e pode ser arrastada).

```
python3 _build/export.py [pasta_com_assets_novos]
```

Esta pasta fica fora do deploy (`.vercelignore`).
