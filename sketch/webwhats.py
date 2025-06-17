'''import webbrowser

numero_destino = "+5551985719957"  # Substitua pelo número desejado
webbrowser.open_new_tab(f"https://web.whatsapp.com/send?phone={numero_destino}")
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def enviar_mensagem_whatsapp(numero, imagem, frase):
    # Abre o navegador (você precisa ter o ChromeDriver instalado)
    driver = webdriver.Chrome()

    # Abre a conversa com o número de telefone
    driver.get(f"https://wa.me/{numero}")

    # Espera o elemento da caixa de mensagem carregar
    wait = WebDriverWait(driver, 10)
    caixa_mensagem = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))

    # Envia a imagem
    driver.find_element(By.XPATH, "//input[@type='file']").send_keys(imagem)

    # Espera a imagem ser enviada
    time.sleep(5)

    # Digita a frase
    caixa_mensagem.send_keys(frase)

    # Envia a mensagem
    caixa_mensagem.send_keys("\n")

# Exemplo de uso
numero_destino = "+11234567890"  # Substitua pelo número desejado
imagem_para_enviar = "caminho/para/imagem.jpg"  # Substitua pelo caminho da imagem
frase_para_enviar = "Olá, tudo bem?"
enviar_mensagem_whatsapp(numero_destino, imagem_para_enviar, frase_para_enviar)

'''
Como instalar o ChromeDriver?
Verifique a versão do seu Chrome: O ChromeDriver precisa ser compatível com a versão do seu navegador. 
Para verificar a versão, abra o Chrome e digite chrome://settings/help na barra de endereço.
Acesse o site de downloads: Vá para o site oficial do ChromeDriver: https://developer.chrome.com/docs/chromedriver/downloads
Escolha a versão correta: Na página de downloads, escolha a versão do ChromeDriver que corresponde à versão do seu Chrome 
e ao seu sistema operacional (Windows, macOS ou Linux).
Baixe e extraia: Baixe o arquivo ZIP e extraia o executável chromedriver.exe (no Windows) ou 
chromedriver (nos outros sistemas) para uma pasta no seu computador.
Adicione ao PATH (opcional): Para facilitar o uso, você pode adicionar a pasta onde você extraiu o ChromeDriver 
ao PATH do seu sistema. Isso permite que você execute o ChromeDriver a partir de qualquer lugar no terminal.
'''