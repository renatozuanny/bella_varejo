# %%
import pandas as pd

print("📦 Ajustando a fábrica de dados para gerar exatamente 100 produtos únicos...")

base_produtos = {
    "Smartphone": [
        {"marca": "Samsung Galaxy", "modelos": ["S24 Ultra", "S24+", "S23 FE", "A55 5G", "A35 5G", "M54 5G", "A15 4G"], "precos": [6899, 5199, 2699, 1999, 1699, 1849, 999]},
        {"marca": "Apple iPhone", "modelos": ["15 Pro Max", "15 Pro", "15", "14", "13", "11", "SE 2022"], "precos": [8299, 6999, 4899, 3999, 3499, 2199, 2799]}
    ],
    "Geladeira": [
        {"marca": "Brastemp", "modelos": ["Frost Free 443L Inox", "Frost Free 375L Branca", "Inverse 460L", "Duplex 375L"], "precos": [4199, 2999, 4899, 3199]},
        {"marca": "Consul", "modelos": ["Frost Free 342L Branca", "Facilite 300L", "Duplex 386L"], "precos": [2599, 1999, 2799]},
        {"marca": "Electrolux", "modelos": ["Frost Free 431L Inox", "Efficient 390L", "French Door 520L"], "precos": [3899, 2899, 6499]}
    ],
    "Air Fryer": [
        {"marca": "Mondial", "modelos": ["Digital Inox 5L", "Family 4L", "Grand Family 5.5L"], "precos": [449, 349, 499]},
        {"marca": "Philips Walita", "modelos": ["Digital 4.1L", "Essential 3.2L", "XL 6.2L"], "precos": [599, 419, 899]},
        {"marca": "Arno", "modelos": ["Fry Fryer Digital 4.2L", "Easy Fry 3.2L", "Ultra Digital 5L"], "precos": [399, 299, 479]}
    ],
    "Notebook": [
        {"marca": "Dell", "modelos": ["Inspiron i5 8GB 512GB", "Vostro i7 16GB 512GB", "G15 Gaming i5"], "precos": [3299, 4599, 4999]},
        {"marca": "Lenovo", "modelos": ["IdeaPad Ryzen 5 8GB", "ThinkPad i5 16GB", "Legion Slim 5"], "precos": [2599, 4199, 7499]},
        {"marca": "Apple", "modelos": ["MacBook Air M2 8GB", "MacBook Pro M3 16GB", "MacBook Air M1 8GB"], "precos": [7999, 14999, 5499]}
    ],
    "Televisor": [
        {"marca": "LG", "modelos": ["Smart TV 4K 50''", "OLED Evo 55''"], "precos": [2499, 5999]},
        {"marca": "Samsung", "modelos": ["Crystal UHD 55''", "QLED 4K 65''"], "precos": [2699, 4499]}
    ]
}

# %%
lista_final = []
contador_id = 1000

for categoria, marcas in base_produtos.items():
    for m in marcas:
        marca_nome = m["marca"]
        for mod, preco_base in zip(m["modelos"], m["precos"]):
            
            # Cores para tech, voltagem para eletrodomésticos
            variacoes = ["Grafite", "Prata", "Branco"] if categoria in ["Smartphone", "Notebook", "Televisor"] else ["110V", "220V"]
            
            for var in variacoes:
                contador_id += 1
                ajuste_preco = 1.03 if var in ["Prata", "220V"] else 1.0
                preco_ref = round(preco_base * ajuste_preco, 2)
                
                item = {
                    "id_produto_interno": f"BV{contador_id}",
                    "nome_produto": f"{marca_nome} {mod} - {var}",
                    "categoria": categoria,
                    "preco_base_referencia": preco_ref,
                    "preco_bella_varejo": ""
                }
                lista_final.append(item)

# Forçando o corte cirúrgico exatamente em 100
df_catalogo = pd.DataFrame(lista_final).head(100)

# %%

nome_arquivo = "catalogo_bella_varejo.xlsx"
df_catalogo.to_excel(nome_arquivo, index=False)

print(f"\n🎉 Agora sim! Planilha '{nome_arquivo}' gerada com EXATAMENTE {len(df_catalogo)} produtos 100% distintos.")
print("Missão atualizada: Pode abrir o arquivo e começar o preenchimento estratégico da coluna 'preco_bella_varejo'!")