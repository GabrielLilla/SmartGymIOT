#include <SPI.h>      // Biblioteca para barramento SPI
#include <MFRC522.h>   // Biblioteca para o leitor RFID

#define SS_PIN 10  // Pino SDA (Slave Select)
#define RST_PIN 9  // Pino de Reset

MFRC522 rfid(SS_PIN, RST_PIN); // Passagem de parâmetros dos pinos

void setup() {
  Serial.begin(9600);   // Inicializa a comunicação Serial
  SPI.begin();          // Inicializa o barramento SPI
  rfid.PCD_Init();      // Inicializa o módulo MFRC522
  
  Serial.println("Aproxime sua tag do leitor...");
}

void loop() {
  // Verifica se há um novo cartão presente
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  // --- BLOCO DE PROCESSAMENTO DO UID ---
  String strID = "";
  for (byte i = 0; i < 4; i++) {
    // Adiciona um zero à esquerda se o byte for menor que 16 (0x10)
    strID += (rfid.uid.uidByte[i] < 0x10 ? "0" : "") + 
             String(rfid.uid.uidByte[i], HEX) + 
             (i != 3 ? " " : "");
  }
  strID.toUpperCase(); // Deixa as letras em maiúsculo
  // --- FIM DO BLOCO ---

  // Saída de dados apenas no Monitor Serial
  //Serial.print("Tag detectada! UID: ");
  Serial.println(strID);

  rfid.PICC_HaltA();       // Para a leitura do cartão
  rfid.PCD_StopCrypto1();  // Interrompe a criptografia no leitor
}
