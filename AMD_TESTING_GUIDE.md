# Dual-Boot-Anleitung: Windows und Ubuntu (mit AMD GPU/ROCm)

Diese Anleitung beschreibt, wie du ein Dual-Boot-System mit Windows und Ubuntu Linux einrichtest, um die volle Leistung deiner AMD GPU mit ROCm nutzen zu können. Ein Dual-Boot-System ermöglicht es dir, beim Starten des Computers zwischen Windows und Ubuntu zu wählen.

**Voraussetzungen:**

*   **Hardware:**
    *   Eine AMD GPU, die von ROCm unterstützt wird (z. B. deine RX 7900 XTX). Überprüfe die [offizielle ROCm-Dokumentation](https://rocm.docs.amd.com/) für die Kompatibilitätsliste.
    *   Einen Computer mit einem 64-Bit-Windows-Betriebssystem (Windows 10 oder 11).
    *   Genügend freier Festplattenspeicher (mindestens 50 GB für Ubuntu, 100 GB oder mehr empfohlen). Es ist *sehr* empfehlenswert, Windows und Ubuntu auf *getrennten physischen Laufwerken* zu installieren, falls möglich (z. B. Windows auf einer SSD, Ubuntu auf einer anderen SSD/HDD).
    *   Ein bootfähiges USB-Laufwerk (mindestens 8 GB).
*   **Software:**
    *   Ein Windows-Installationsmedium (falls du Windows neu installieren musst).
    *   Ein Ubuntu Desktop ISO-Image (LTS-Version empfohlen): [https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop)
    *   Ein Tool zum Erstellen eines bootfähigen USB-Laufwerks (z. B. Rufus, balenaEtcher, UNetbootin).

**Wichtige Vorbereitungen (bevor du beginnst!):**

*   **Daten sichern:** **Sichere unbedingt alle wichtigen Daten von deinem Computer, bevor du fortfährst!**  Partitionierungsänderungen und Betriebssysteminstallationen bergen immer das Risiko von Datenverlust. Sichere deine Daten auf einer externen Festplatte, in der Cloud oder an einem anderen sicheren Ort.
*   **Windows-BitLocker deaktivieren (falls aktiviert):** Wenn du BitLocker-Verschlüsselung auf deinem Windows-Laufwerk verwendest, *deaktiviere BitLocker unbedingt*, *bevor* du mit der Installation von Ubuntu beginnst.  Andernfalls kann es zu Problemen beim Zugriff auf deine Windows-Partition kommen. Gehe zu "Systemsteuerung" -> "System und Sicherheit" -> "BitLocker-Laufwerkverschlüsselung" und deaktiviere BitLocker für dein Windows-Laufwerk. Du benötigst deinen BitLocker-Wiederherstellungsschlüssel.
* **Fast Startup in Windows deaktivieren**: Fast Startup kann dazu führen, dass der Rechner nicht vollständig herunterfährt, und das kann beim Dual-Boot zu Problemen führen, insbesondere mit Dateisystemen. Gehe zu "Systemsteuerung" -> "Hardware und Sound" -> "Energieoptionen" -> "Auswählen, was beim Drücken von Netzschaltern geschehen soll" -> "Einstellungen ändern, die momentan nicht verfügbar sind" -> Entferne den Haken bei "Schnellstart aktivieren (empfohlen)".
*   **UEFI-Einstellungen überprüfen (Secure Boot):**
    *   Stelle sicher, dass dein Computer im UEFI-Modus (nicht im Legacy-BIOS-Modus) bootet.  Die meisten modernen Computer verwenden UEFI.
    *   **Secure Boot:**  Du *musst* Secure Boot *möglicherweise* deaktivieren, um Ubuntu zu installieren und zu booten.  Allerdings ist es *empfehlenswert*, Secure Boot *aktiviert* zu lassen, wenn möglich.  Viele aktuelle Ubuntu-Versionen unterstützen Secure Boot.  Probiere es zuerst *mit* aktiviertem Secure Boot. Wenn es Probleme gibt, deaktiviere es *vorübergehend* während der Installation und versuche dann, es nach der Installation und Einrichtung des Bootloaders wieder zu aktivieren.  Die genaue Vorgehensweise zum Deaktivieren/Aktivieren von Secure Boot hängt von deinem Mainboard/BIOS ab.  Suche im BIOS/UEFI-Setup nach Optionen wie "Secure Boot", "Boot Mode", "OS Type".
*   **Festplattenkonfiguration überprüfen (GPT vs. MBR):**  Es wird dringend empfohlen, dass sowohl Windows als auch Ubuntu auf Laufwerken mit GPT-Partitionstabelle installiert werden (nicht MBR).  Überprüfe dies in der Windows-Datenträgerverwaltung ("Datenträgerverwaltung" in der Suche eingeben). Rechtsklicke auf deine Festplatte -> "Eigenschaften" -> "Volumes" -> "Partitionsstil".  Wenn dort "GUID-Partitionstabelle (GPT)" steht, ist alles in Ordnung.  Wenn dort "Master Boot Record (MBR)" steht, ist es *dringend* empfohlen, vor der Dual-Boot-Installation eine Konvertierung zu GPT durchzuführen (Daten sichern!).  Windows bietet das Tool `mbr2gpt.exe` für die Konvertierung an.
* **Freien Speicherplatz schaffen**: Stelle sicher, dass du genügend *nicht zugewiesenen* Speicherplatz auf der Festplatte hast, auf der du Ubuntu installieren möchtest. Du kannst in der Windows-Datenträgerverwaltung Partitionen verkleinern, um Platz zu schaffen. Es ist sehr ratsam, getrennte Festplatten zu nutzen, wenn möglich.

**Schritte:**

1.  **Bootfähiges Ubuntu-USB-Laufwerk erstellen:**

    *   Lade das Ubuntu Desktop ISO-Image herunter.
    *   Lade Rufus (oder ein anderes Tool) herunter: [https://rufus.ie/](https://rufus.ie/)
    *   Stecke das USB-Laufwerk in deinen Computer.
    *   Starte Rufus.
        *   **Device:** Wähle dein USB-Laufwerk aus.
        *   **Boot selection:** Wähle "Disk or ISO image (Please select)" und klicke auf "SELECT", um die Ubuntu ISO-Datei auszuwählen.
        *   **Partition scheme:** Wähle "GPT" (sehr wichtig, wenn dein System UEFI verwendet).
        *   **Target system:** Wähle "UEFI (non CSM)".
        *   **File system:** Wähle "FAT32".
        *   Klicke auf "START".  **Achtung:**  Alle Daten auf dem USB-Laufwerk werden gelöscht!

2.  **Vom USB-Laufwerk booten:**

    *   Starte deinen Computer neu.
    *   Rufe das Boot-Menü deines Computers auf.  Die Taste, die du drücken musst, variiert je nach Hersteller (oft `F2`, `F10`, `F11`, `F12`, `Entf`, `Esc`).  Suche nach einer Meldung wie "Press [Taste] to enter setup" oder "Press [Taste] to select boot device" beim Starten.
    *   Wähle dein USB-Laufwerk als Boot-Gerät aus.

3.  **Ubuntu installieren:**

    *   Wähle im Ubuntu-Boot-Menü "Try or Install Ubuntu".
    *   Wähle deine Sprache und klicke auf "Install Ubuntu".
    *   Wähle deine Tastaturbelegung.
    *   Wähle "Normale Installation" (oder "Minimale Installation", wenn du Platz sparen möchtest – installiere dann aber später die benötigten Pakete nach).
    *   **WICHTIG: Installationsart:**
        *   **Option 1 (Empfohlen – Separate Festplatte):** Wenn du Ubuntu auf einer *separaten* physischen Festplatte installierst, wähle "Etwas Anderes" ("Something else").  Wähle die *richtige* Festplatte aus (die *nicht* deine Windows-Festplatte ist!).  Erstelle auf dieser Festplatte:
            *   Eine EFI-Systempartition (ESP), falls noch keine vorhanden ist (ca. 512 MB, FAT32, Mount-Punkt `/boot/efi`). Diese Partition ist *essentiell* für UEFI-Systeme.
            *   Eine Root-Partition (`/`, ext4, mindestens 30 GB, besser 50 GB oder mehr).
            *   Optional: Eine separate `/home`-Partition (ext4, für deine Benutzerdaten).
            *   Optional: Eine Swap-Partition (swap, Größe etwa so groß wie dein RAM).
        *   **Option 2 (Einzelne Festplatte – Riskanter):** Wenn du Ubuntu auf *derselben* physischen Festplatte wie Windows installierst, wähle ebenfalls "Etwas Anderes" ("Something else").  Sei *extrem vorsichtig*, die richtige Partition auszuwählen!  Du musst eine vorhandene Partition (wahrscheinlich eine deiner Windows-Partitionen) *verkleinern*, um Platz für Ubuntu zu schaffen. *Verkleinere niemals die Windows-Systempartition (normalerweise C:) zu stark!* Erstelle dann die benötigten Partitionen (ESP, Root, optional Home, optional Swap) im *freien Speicherplatz*.
        *   **Wähle *niemals* "Install Ubuntu alongside Windows Boot Manager"**, wenn du die volle Kontrolle über die Installation haben und Probleme vermeiden möchtest. Diese Option kann unvorhersehbare Ergebnisse liefern.
    *   **Bootloader-Installation:** Stelle sicher, dass der Bootloader (GRUB) auf der *richtigen* Festplatte installiert wird.  Wenn du Ubuntu auf einer separaten Festplatte installierst, wähle diese Festplatte aus. Wenn du Ubuntu auf derselben Festplatte wie Windows installierst, wähle die Festplatte aus, die die EFI-Systempartition enthält (normalerweise die, auf der auch Windows installiert ist).
    *   Wähle deine Zeitzone.
    *   Erstelle einen Benutzeraccount.
    *   Warte, bis die Installation abgeschlossen ist, und starte deinen Computer neu.

4.  **Boot-Reihenfolge anpassen (falls nötig):**

    *   Nach dem Neustart solltest du das GRUB-Bootmenü sehen, in dem du zwischen Ubuntu und Windows wählen kannst.
    *   Falls Windows nicht automatisch startet oder du die Standard-Boot-Reihenfolge ändern möchtest, rufe das BIOS/UEFI-Setup deines Computers auf (siehe Schritt 2) und passe die Boot-Reihenfolge an.

5.  **AMD GPU-Treiber und ROCm installieren (in Ubuntu):**

    *   Öffne ein Terminal in Ubuntu.
    *   Folge der *offiziellen* AMD ROCm-Installationsanleitung für deine Ubuntu-Version: [https://rocm.docs.amd.com/en/latest/deploy/linux/install_overview.html](https://rocm.docs.amd.com/en/latest/deploy/linux/install_overview.html)
    *   **Wichtig:** Die offizielle Anleitung beinhaltet das Hinzufügen des AMD-Repositorys, das Installieren der `amdgpu-install`-Skripte und die Verwendung dieser Skripte zur Installation der ROCm-Komponenten.  Dies stellt sicher, dass du die *aktuellsten* Treiber und ROCm-Versionen erhältst.
    * Ein typischer Installationsbefehl (nach dem Hinzufügen des Repos) könnte so aussehen (passe ihn an die Anweisungen auf der AMD-Seite an):
      ```bash
      sudo amdgpu-install --usecase=rocm,hip,dkms
      ```

6.  **Benutzer zur `video` und `render` Gruppe hinzufügen:**

    ```bash
    sudo usermod -a -G video $LOGNAME
    sudo usermod -a -G render $LOGNAME
    ```
    Melde dich ab und wieder an, damit die Gruppenänderungen wirksam werden.

7.  **ROCm-Umgebung überprüfen:**
    * Führe `rocminfo` und `hipconfig --full` aus, um die Installation zu überprüfen (siehe vorherige Anleitung).

8.  **PyTorch (ROCm-Version) installieren:**
    *   Folge den Anweisungen auf der PyTorch-Website, um die ROCm-Version zu installieren (siehe vorherige Anleitung).

9.  **Transformers und andere Bibliotheken installieren:**
     ```bash
     pip3 install transformers sentence-transformers chromadb bitsandbytes
     ```

**Troubleshooting:**

*   **Kein GRUB-Menü:** Wenn du nach der Installation von Ubuntu direkt in Windows bootest, wurde der Bootloader möglicherweise nicht korrekt installiert.  Du kannst versuchen, GRUB mit einem Live-Ubuntu-System (vom USB-Laufwerk) zu reparieren.  Es gibt Tools wie `boot-repair`, die dabei helfen können.
*   **Windows startet nicht mehr:** Wenn Windows nicht mehr startet, hast du möglicherweise versehentlich die Windows-Boot-Partition beschädigt.  Du kannst versuchen, die Windows-Startreparatur mit einem Windows-Installationsmedium durchzuführen.
*   **ROCm-Probleme:** Wenn du Probleme mit ROCm hast (Fehler in `rocminfo`), überprüfe die ROCm-Dokumentation und stelle sicher, dass du die richtigen Treiber und ROCm-Versionen für deine GPU und Ubuntu-Version installiert hast.
* **Secure Boot Probleme:** Sollte Ubuntu nicht starten, deaktiviere Secure Boot vorübergehend, und versuche es danach wieder zu aktivieren.

Diese Anleitung bietet eine detaillierte Vorgehensweise für die Einrichtung eines Dual-Boot-Systems. Beachte jedoch, dass die genauen Schritte je nach deiner Hardwarekonfiguration leicht variieren können.  Es ist immer ratsam, die Dokumentation deines Mainboard-Herstellers und die offiziellen Anleitungen von Ubuntu und AMD ROCm zu konsultieren.