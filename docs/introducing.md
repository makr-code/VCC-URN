
Föderierte Graph-RAG-Architektur für die deutsche Verwaltungslandschaft: Ein technisches und strategisches Konzept

Executive Summary
Die föderale Struktur Deutschlands stellt die Digitalisierung der öffentlichen Verwaltung vor eine einzigartige Herausforderung: die Notwendigkeit, isolierte, aber hoheitliche Datenbestände der 16 Bundesländer intelligent zu vernetzen, um komplexe, länderübergreifende Sachverhalte effizient bearbeiten zu können. Gleichzeitig muss die verfassungsrechtlich verankerte Datenhoheit der Länder gewahrt bleiben.1 Dieser Bericht entwirft eine Vision und ein technisches Konzept zur Lösung dieses Problems durch die Schaffung eines virtuellen, gesamtstaatlichen Wissensgraphen. Dieser entsteht nicht durch physische Datenreplikation, sondern durch eine intelligente Föderationsschicht. Eine Anfrage in einem Bundesland kann somit nahtlos auf referenzierte Daten in einem anderen zugreifen, ohne dass der Endanwender die Komplexität der dahinterliegenden verteilten Architektur bemerkt.
Der architektonische Kernansatz basiert auf einer föderierten Architektur, die auf drei Säulen ruht: erstens, einem global eindeutigen Identifikationsschema auf Basis von Uniform Resource Names (URNs) für alle Verwaltungsobjekte; zweitens, der virtuellen Verknüpfung dieser Objekte über sogenannte Proxy-Knoten in den lokalen Wissensgraphen der Länder; und drittens, einer zentralen Gateway-Schicht, die Abfragen über die Landesgrenzen hinweg orchestriert und Ergebnisse aggregiert.
Die strategische Empfehlung lautet, die Implementierung eines solchen Systems als ein zentrales Vorhaben der Verwaltungsdigitalisierung zu verstehen. Es muss eng mit bestehenden Initiativen wie der „Deutschen Verwaltungscloud-Strategie“ und dem „Deutschland-Stack“ verzahnt und durch ein starkes, föderales Governance-Gremium, analog zum IT-Planungsrat, gesteuert werden.2 Dieses Konzept stellt einen Weg dar, die Prinzipien des Föderalismus mit den technologischen Notwendigkeiten des 21. Jahrhunderts in Einklang zu bringen und eine souveräne, intelligente und vernetzte Verwaltung für Deutschland zu schaffen.

Teil I: Das Fundament – Die autonome Landesinstanz als prozessbewusster "Digitaler Zwilling"

Die Realisierung eines föderierten Netzwerks setzt voraus, dass jede einzelne teilnehmende Einheit – in diesem Fall die RAG-Instanz eines Bundeslandes – eine in sich geschlossene, leistungsfähige und souveräne Zelle darstellt. Diese autonomen Landesinstanzen bilden das Fundament, auf dem die föderale Vernetzung aufbaut. Ihre Architektur muss daher nicht nur die lokalen Anforderungen erfüllen, sondern bereits die technischen Voraussetzungen für eine spätere, nahtlose Integration schaffen.

1.1 Das VCC/VPB-Ökosystem: Die souveräne Zelle des Föderationsnetzwerks

Jede der 16 Landesinstanzen wird als eigenständiges VCC/VPB-Ökosystem (Veritas, Covina, Clara / Verwaltungsprozess-Backbone) konzipiert.1 Diese Architektur fungiert als „Digitaler Zwilling“ des jeweiligen landesspezifischen Verwaltungsprozesses und bildet dessen rechtliche und prozedurale Realität in einem maschinenlesbaren Format ab. Der Kern jeder Instanz ist eine fortschrittliche Graph-RAG-Architektur (Retrieval-Augmented Generation). Diese kombiniert die semantische Suche in unstrukturierten Dokumenten, ermöglicht durch Vektor-Datenbanken, mit dem strukturierten Kontextwissen einer Graph-Datenbank.1 Dieser hybride Ansatz überwindet die entscheidende Schwäche herkömmlicher RAG-Systeme, die zwar inhaltlich ähnliche Textabschnitte finden, aber keine expliziten, logischen Beziehungen zwischen Informationen verstehen – beispielsweise, dass ein bestimmtes Gutachten die Grundlage für eine spezifische Genehmigungsauflage war.1
Die Konzeption jeder Landesinstanz als autonomes und voll funktionsfähiges System ist die unabdingbare Voraussetzung für die Akzeptanz in der föderalen Struktur Deutschlands. Sie stellt sicher, dass jedes Land die volle Souveränität und Kontrolle über seine eigenen Daten und Verwaltungsprozesse behält, was einen entscheidenden Unterschied zu jedem zentralisierten Ansatz darstellt, bei dem Daten an eine übergeordnete Stelle abgegeben werden müssten.2

1.2 Die Unified Database Strategy (UDS3): Polyglot Persistence als lokales Optimierungsprinzip

Das technologische Herzstück jeder Landesinstanz ist die „Unified Database Strategy“ (UDS3), eine konkrete Implementierung des Architekturprinzips der „Polyglot Persistence“.1 Dieses Prinzip, das von Vordenkern wie Martin Fowler geprägt wurde, besagt, dass für unterschiedliche Datentypen und Anwendungsfälle die jeweils am besten geeignete Speichertechnologie verwendet werden sollte, anstatt zu versuchen, alle Daten in ein einziges, unflexibles Datenbanksystem zu zwingen.6 Die UDS3 kombiniert drei spezialisierte Datenbanktypen, um eine optimale Balance aus Kontextverständnis, semantischer Suche und transaktionaler Integrität zu erreichen:
Rolle der Graph-Datenbank (z.B. Neo4j): Sie fungiert als das „digitale Nervensystem“ der Verwaltung.1 Hier werden die expliziten Beziehungen zwischen allen relevanten Entitäten – Gesetze, Anlagen, Betreiber, Dokumente, Verfahrensschritte – als Knoten und Kanten modelliert. Sie liefert den unverzichtbaren Kontext, der eine reine Textsuche in die Lage versetzt, die Relevanz von Informationen im Gesamtprozess zu verstehen. Eine Abfrage kann hier logischen Pfaden folgen, wie z.B. von einem :Genehmigungsbescheid zu allen darin enthaltenen :Auflagen und den zugrundeliegenden :Gutachten.1
Rolle der Vektor-Datenbank (z.B. ChromaDB, Qdrant): Diese Datenbank ist auf die Speicherung und extrem schnelle Abfrage von hochdimensionalen Vektoren spezialisiert. Unstrukturierte Dokumentinhalte werden in Textabschnitte zerlegt und in numerische Vektoren (Embeddings) umgewandelt. Bei einer Anfrage ermöglicht dies eine blitzschnelle semantische Ähnlichkeitssuche, um die inhaltlich relevantesten Textpassagen als Kontext für das Sprachmodell zu finden.
Rolle der relationalen Datenbank (z.B. PostgreSQL): Während Graph- und Vektor-Datenbanken die Kernintelligenz des RAG-Prozesses bilden, eignet sich eine relationale Datenbank hervorragend für die Verwaltung hochstrukturierter, transaktionaler Daten. Dazu gehören Metadaten zu Dokumenten (Erstelldatum, Autor), der Status von Verarbeitungspipelines, detaillierte Audit-Logs über Systemzugriffe und Nutzeranfragen sowie die Verwaltung von Benutzerkonten und Berechtigungen.5
Die Anwendung des Polyglot-Persistence-Prinzips auf der Ebene der einzelnen Landesinstanz schafft eine interne, technische Heterogenität, die auf maximale Leistung und Effizienz optimiert ist. Diese Komplexität muss jedoch nach außen verborgen werden, um eine stabile und klar definierte Schnittstelle für die föderale Vernetzung zu bieten.6 Die Architektur folgt somit einem Muster, das sich auf höheren Ebenen wiederholt: die Beherrschung von Heterogenität durch die Schaffung von Abstraktionsebenen. Die Lehren aus der Integration dieser drei Datenbanktypen innerhalb einer Instanz sind direkt auf die Herausforderungen bei der Integration der 16 Instanzen auf Bundesebene übertragbar.

1.3 Die Covina-Ingestion-Pipeline: Automatisierte Wissensgenerierung

Die Befüllung der UDS3-Datenbanken erfolgt hochautomatisiert durch die „Covina“-Ingestion-Pipeline. Diese ist als ereignisgesteuerte Microservice-Architektur konzipiert, in der spezialisierte Software-Agenten („Worker“) definierte Aufgaben ausführen.1 Ein OCR-Worker wandelt gescannte Dokumente in Text um, ein DSGVO-Worker anonymisiert personenbezogene Daten, und ein LLM-Worker kann Zusammenfassungen erstellen.1
Für die föderale Vernetzung ist der Relations Worker von entscheidender Bedeutung. Seine Aufgabe ist es, mittels Natural Language Processing (NLP) Entitäten und deren Beziehungen aus den Texten zu extrahieren.1 Im Kontext der Föderation muss dieser Worker darauf trainiert werden, nicht nur lokale Entitäten zu erkennen, sondern auch explizite externe Referenzen zu identifizieren. Erkennt er beispielsweise in einem bayerischen Gutachten ein Aktenzeichen, das eindeutig einer nordrhein-westfälischen Behörde zuzuordnen ist, muss er dies als potenziellen Verknüpfungspunkt für den föderierten Graphen markieren.3
An diesem Punkt des Prozesses wird auch das Fundament für die globale Adressierbarkeit gelegt. Der logischste Zeitpunkt zur Erzeugung eines global eindeutigen Identifikators für ein neues Datenobjekt ist unmittelbar zu Beginn der Covina-Pipeline. Sobald der File Scanner Worker ein neues Dokument erfasst, sollte eine eindeutige Kennung generiert werden, noch bevor die weitere Verarbeitung und Verteilung durch den UDS3 Backend Worker auf die verschiedenen Datenbanken erfolgt.5 Die Verwendung einer Universally Unique Identifier (UUID) an dieser Stelle stellt sicher, dass das Objekt über seinen gesamten Lebenszyklus und über alle internen Speichersysteme hinweg eine konsistente und eindeutige Kennung besitzt, die später zur Grundlage des globalen URN-Schemas wird.

Teil II: Die föderale Herausforderung – Vernetzung von 16 souveränen Datendomänen

Die Vernetzung von 16 autonomen RAG-Instanzen ist weniger eine technische als vielmehr eine politisch-organisatorische Herausforderung, die durch die Prinzipien des deutschen Föderalismus geprägt ist. Jede technische Lösung muss die Souveränität der Länder als oberste Prämisse anerkennen.

2.1 Das Prinzip der Datensouveränität im Föderalismus

Datensouveränität bedeutet für eine öffentliche Verwaltung die Fähigkeit, die vollständige Kontrolle darüber auszuüben, welche Daten wie, von wem und zu welchem Zweck genutzt werden.4 Im deutschen Föderalismus ist dies keine bloße technische Präferenz, sondern eine nicht verhandelbare rechtliche und politische Anforderung, die sich aus der Kompetenzverteilung zwischen Bund und Ländern ergibt.11
In diesem Kontext agiert jede Landesinstanz als eine autonome Datendomäne. Dieses Konzept ist analog zum Architekturparadigma des „Data Mesh“, bei dem dezentrale, fachlich orientierte Teams die volle Verantwortung für ihre „Datenprodukte“ übernehmen – von der Erfassung über die Qualitätssicherung bis zur Bereitstellung über definierte Schnittstellen.13 Jedes Bundesland ist somit der alleinige „Owner“ seiner Verwaltungsdaten.

2.2 Architektonische Paradigmen im Vergleich: Föderation als einziger gangbarer Weg

Angesichts der Anforderung der Datensouveränität lassen sich drei grundlegende Architekturmuster für die Datenintegration bewerten:
Zentralisierung (Data Warehouse / Data Lake): Bei diesem Ansatz werden alle relevanten Daten aus den 16 Ländern in ein einziges, zentrales System (z.B. beim Bund) repliziert. Dieser Ansatz ist für die öffentliche Verwaltung in Deutschland inakzeptabel. Er verletzt direkt das Prinzip der Datensouveränität, schafft einen massiven Single Point of Failure und erzeugt einen kaum zu bewältigenden Governance-Overhead, da eine zentrale Stelle die Verantwortung für die Daten aller Länder übernehmen müsste.15
Replikation/Synchronisation: Daten werden regelmäßig zwischen den 16 Instanzen kopiert. Dieser Ansatz führt zu massiver Datenredundanz, hohen Speicherkosten und erheblicher Netzwerklast. Noch gravierender sind die Konsistenzprobleme: Es entsteht die Gefahr von „stale data“, also veralteten Datenkopien, und es ist oft unklar, welche Instanz die verbindliche „Source of Truth“ für einen bestimmten Datensatz ist.15
Datenföderation (Virtuelle Integration): Bei diesem Ansatz verbleiben die Daten an ihrem Ursprungsort in der jeweiligen Landesinstanz. Eine virtuelle Abstraktionsschicht ermöglicht es, eine einheitliche, gesamtstaatliche Sicht auf die verteilten Daten zu erzeugen und Abfragen in Echtzeit über die Landesgrenzen hinweg auszuführen, ohne die Daten physisch zu bewegen.15 Dies ist der einzige architektonische Ansatz, der die Kernanforderung der föderalen Datensouveränität vollständig erfüllt.
Die folgende Tabelle fasst die Bewertung dieser Strategien zusammen und verdeutlicht die Eignung der Datenföderation für den gegebenen Anwendungsfall.
Bewertungskriterium
Zentralisierung (Data Warehouse)
Replikation/Synchronisation
Datenföderation (Virtuelle Integration)
Datensouveränität
Verletzt (Daten verlassen Hoheitsbereich)
Kompromittiert (Kontrollverlust über Kopien)
Gewährleistet (Daten verbleiben im Ursprungssystem)
Datenaktualität
Gering (abhängig von ETL-Zyklen)
Mittel bis Gering (Risiko von "stale data")
Hoch (Echtzeit-Zugriff auf Quelldaten)
Speicherkosten
Sehr hoch (vollständige Duplizierung)
Sehr hoch (multiple Duplizierung)
Minimal (nur Metadaten/Referenzen)
Netzwerklast
Hoch (bei ETL-Prozessen)
Sehr hoch (kontinuierliche Synchronisation)
Gering (nur für Abfragen und Ergebnisse)
Konsistenzmanagement
Zentralisiert, aber komplex
Extrem komplex (N-zu-N-Synchronisation)
Vereinfacht ("Single Source of Truth" pro Domäne)
Implementierungskomplexität
Hoch (zentrale Infrastruktur)
Sehr hoch (komplexe Sync-Logik)
Mittel (Fokus auf Föderationsschicht)


2.3 Kernanforderungen an ein föderiertes RAG-Netzwerk

Aus der Entscheidung für eine Föderationsarchitektur leiten sich vier zentrale technische und organisatorische Kernanforderungen ab, die erfüllt sein müssen:
Globale Adressierbarkeit: Jedes relevante Verwaltungsobjekt – sei es ein Dokument, eine Akte, ein Unternehmen oder eine genehmigte Anlage – im gesamten Bundesgebiet muss über einen eindeutigen, persistenten und ortsunabhängigen Identifikator referenzierbar sein.
Interoperabilität der Schnittstellen: Die APIs der 16 Landesinstanzen müssen einem gemeinsamen, standardisierten Vertrag folgen. Nur so kann die übergeordnete Föderationsschicht Anfragen einheitlich formulieren und an die zuständigen Instanzen weiterleiten.
Domänenübergreifende Sicherheit: Es muss ein föderiertes Identitäts- und Zugriffsmanagementsystem etabliert werden. Dieses muss sicherstellen, dass ein authentifizierter Nutzer aus einer Behörde in Bundesland A nur auf diejenigen Daten in Bundesland B zugreifen kann, für die er eine explizite Autorisierung besitzt.
Föderierte Governance: Ein übergeordnetes, kooperatives Gremium ist erforderlich, um gemeinsame Regeln, Datenstandards und Ontologien zu definieren und fortzuschreiben. Dies ist die Voraussetzung für die semantische Interoperabilität, also das gemeinsame Verständnis der Bedeutung von Daten über Systemgrenzen hinweg.

Teil III: Architektonischer Entwurf – Ein föderierter Wissensgraph über virtuelle Verknüpfungen

Der Kern der technischen Lösung besteht darin, die 16 autonomen Wissensgraphen der Länder virtuell zu einem gesamtstaatlichen Graphen zu verbinden. Dies geschieht nicht durch das Zusammenführen der Datenbanken, sondern durch die Etablierung eines intelligenten Referenzierungs- und Abfragesystems.

3.1 Das Fundament der Verknüpfung: Ein URN-basiertes globales Identifikationsschema

Das grundlegendste Problem bei der Verknüpfung verteilter Systeme ist die eindeutige und dauerhafte Adressierung von Datenobjekten. Wie kann ein Dokument in Bayern von einem System in Nordrhein-Westfalen so referenziert werden, dass diese Referenz auch nach Jahren oder nach einer Systemmigration noch gültig ist?
Problem mit bestehenden Identifikatoren: Herkömmliche Methoden sind hierfür ungeeignet. Datenbank-interne IDs sind nicht global eindeutig. URLs (Uniform Resource Locators) sind an den Speicherort gebunden und brechen, wenn sich dieser ändert. Reine UUIDs (Universally Unique Identifiers) sind zwar global eindeutig, aber semantisch leer; sie enthalten keine Information über den Kontext oder die Herkunft des Objekts.20
Lösung durch URNs: Die Lösung liegt in der Einführung eines standardisierten Schemas für Uniform Resource Names (URNs). Gemäß den Internetstandards RFC 2141 und dem neueren RFC 8141 identifizieren URNs eine Ressource dauerhaft und ortsunabhängig, indem sie ihr einen Namen innerhalb eines definierten Namespace geben.22
Vorgeschlagene Syntax für die deutsche Verwaltung: Eine spezifische Syntax für Verwaltungsdaten könnte wie folgt aussehen, um sowohl Maschinenlesbarkeit als auch menschliche Interpretierbarkeit zu gewährleisten:
urn:de:<Länderkürzel>:<Fachdomäne>:<Objekttyp>:<LokalesAktenzeichen>:<UUID>
urn:de: Der globale Namespace, der alle Daten der deutschen Verwaltung umfasst.
<Länderkürzel>: Ein zweistelliges Kürzel für das Bundesland (z.B. by für Bayern, nrw für NRW), das die datenhaltende Hoheit klarstellt.
<Fachdomäne>: Ein Kürzel für den fachlichen Kontext (z.B. bimschg für Immissionsschutz, bau für Baurecht), das die thematische Einordnung ermöglicht.
<Objekttyp>: Definiert die Art des Objekts (z.B. anlage, bescheid, gutachten).
<LokalesAktenzeichen>: Das bereits existierende, menschenlesbare Aktenzeichen des Ursprungssystems, das URL-kodiert wird, um Sonderzeichen sicher zu übertragen.24
<UUID>: Eine bei der Ersterfassung des Objekts generierte UUID, die absolute Eindeutigkeit über alle Systeme und Zeiten hinweg garantiert.20
Ein konkretes Beispiel wäre: urn:de:nrw:bimschg:anlage:4711-0815-K1:6e8bc430-9c3a-11d9-9669-0800200c9a66. Diese URN wird, wie in Teil I beschrieben, bei der initialen Erfassung in der Covina-Pipeline generiert und dient als primärer, unveränderlicher Schlüssel für das Datenobjekt über alle Datenbanken der UDS3 hinweg.5 Ohne ein solches globales Namensschema wäre eine skalierbare und wartbare Föderation unmöglich, da jede Punkt-zu-Punkt-Integration auf proprietären, brüchigen Schlüsseln basieren würde, was letztlich zu einem schwer wartbaren „verteilten Monolithen“ führen würde. Die URN ist der technische Schlüssel zur Entkopplung.

3.2 Virtuelle Integration durch Proxy-Knoten im Wissensgraphen

Die global eindeutigen URNs ermöglichen es, Objekte über Systemgrenzen hinweg zu referenzieren, ohne sie zu kopieren. Dies wird im lokalen Wissensgraphen jeder Landesinstanz durch das Konzept der Proxy-Knoten (auch als Schatten- oder Stub-Knoten bezeichnet) umgesetzt.
Wenn beispielsweise die Covina-Pipeline in Bayern ein Dokument verarbeitet, das auf die oben genannte Anlage in NRW verweist, wird im bayerischen Graphen kein vollständiger Datenknoten für diese Anlage erstellt. Stattdessen wird ein schlanker Proxy-Knoten angelegt, der als lokaler Stellvertreter für das externe Objekt fungiert. Dieser Knoten enthält nur die absolut notwendigen Informationen:
Ein spezifisches Label, z.B. :ProxyAnlage oder ein Standardlabel mit einer Eigenschaft wie :Anlage {is_proxy: true}.
Die globale urn als primäre Eigenschaft, die die eindeutige Referenz auf das Originalobjekt in NRW herstellt.
Optional minimale, aus dem Kontext extrahierte Metadaten wie den Namen der Anlage.
Dieser Proxy-Knoten agiert als lokaler Ankerpunkt im Graphen. Eine Kante, wie z.B. (:Gutachten)-->(:ProxyAnlage), kann nun ein lokales Objekt (das Gutachten in Bayern) mit der logischen Repräsentation des externen Objekts (der Anlage in NRW) verbinden. Die eigentlichen Detaildaten der Anlage verbleiben dabei vollständig und ausschließlich in der Hoheit der NRW-Instanz.

3.3 Die Föderationsschicht: Muster für die verteilte Abfrage

Stellt ein Nutzer in Bayern eine Anfrage, die ein externes Objekt betrifft (z.B. „Zeige mir alle Gutachten zur Anlage ‚Chemiewerk Wesseling‘“), erkennt das bayerische System am Proxy-Knoten und dessen URN (urn:de:nrw:...), dass die Stammdaten in NRW liegen. An dieser Stelle muss die Föderationsschicht die Abfrage über die Landesgrenze hinweg koordinieren. Hierfür gibt es zwei grundlegende Architekturmuster:
Muster 1: Zentraler Query Broker (Gateway-Architektur / Orchestrierung): In diesem Modell gibt es eine zentrale Komponente, den „Föderations-Gateway“, der als einziger logischer Zugangspunkt zum gesamten föderierten Netzwerk fungiert. Die Abfrage wird orchestriert: Die bayerische Instanz sendet eine Anfrage an den Gateway, der diese an die zuständige NRW-Instanz weiterleitet. Die NRW-Instanz löst die Anfrage intern auf, liefert die Daten an den Gateway zurück, welcher sie wiederum an die bayerische Instanz übermittelt.
Eine technologisch ideale Umsetzung dieses Musters ist GraphQL Federation. Jede Landesinstanz stellt einen standardisierten GraphQL-Endpunkt (einen „Subgraph“) bereit. Ein zentraler GraphQL-Gateway (z.B. mit Apollo Federation) komponiert diese 16 Subgraphs zu einem einzigen, virtuellen „Supergraph“. Der Client stellt eine einzige Anfrage an den Gateway, der intelligent die notwendigen Sub-Anfragen an die jeweiligen Landesinstanzen plant, ausführt und die Ergebnisse aggregiert.
Muster 2: Dezentrales Peer-to-Peer-Netzwerk (Choreographie): In diesem Modell gibt es keinen zentralen Koordinator. Jede Landesinstanz kennt die Endpunkte der anderen 15 Instanzen und kommuniziert direkt mit ihnen. Im obigen Beispiel würde die bayerische Instanz die nrw-URN erkennen und eine direkte API-Anfrage an den bekannten Endpunkt der NRW-Instanz stellen. Dieses Muster bietet eine höhere Ausfallsicherheit, da es keinen Single Point of Failure gibt. Allerdings führt es zu einer exponentiell höheren Komplexität in den Bereichen Sicherheit, Monitoring, Auditierung und Governance, da potenziell  Punkt-zu-Punkt-Beziehungen und deren Zugriffsregeln verwaltet werden müssen.
Für den Einsatz im öffentlichen Sektor, wo zentrale Auditierbarkeit, klare Verantwortlichkeiten und durchsetzbare Sicherheitsrichtlinien von höchster Bedeutung sind, ist das Gateway-Modell trotz des Risikos eines zentralen Ausfallpunktes (welches durch moderne Hochverfügbarkeitsarchitekturen mitigiert werden kann) klar überlegen.
Bewertungskriterium
Gateway / Orchestrierung
Peer-to-Peer / Choreographie
Skalierbarkeit
Hoch (Gateway kann skaliert werden)
Sehr hoch (kein zentraler Flaschenhals)
Ausfallsicherheit
Geringer (Gateway als Single Point of Failure)
Hoch (kein zentraler Ausfallpunkt)
Implementierungskomplexität
Mittel (Fokus auf Gateway und Standards)
Sehr hoch (N x N Verbindungen und Logik)
Sicherheit (Kontrolle)
Hoch (zentraler Policy Enforcement Point)
Gering (dezentrale, komplexe Kontrolle)
Auditierbarkeit/Monitoring
Hoch (zentraler Punkt für Logging)
Sehr gering (verteilte, schwer zu korrelierende Logs)
Governance-Durchsetzung
Einfach (Regeln werden im Gateway implementiert)
Sehr schwer (Regeln müssen in jeder Instanz implementiert werden)


Teil IV: Governance und Betrieb eines föderierten Ökosystems

Eine funktionierende technische Föderation erfordert zwingend eine korrespondierende organisatorische und prozessuale Föderation. Die größten Herausforderungen liegen nicht im Code, sondern in der Schaffung gemeinsamer Regeln für Identität, Zugriff, Datenstandards und transaktionale Konsistenz.

4.1 Föderiertes Identitäts- und Zugriffsmanagement (IAM)

Eine der kritischsten Fragen ist die sichere und nachvollziehbare Autorisierung von Zugriffen über Ländergrenzen hinweg. Ein Sachbearbeiter aus Bayern, der eine länderübergreifende Abfrage startet, muss sich gegenüber der Instanz in NRW sicher authentifizieren und nachweisen, dass er für den Zugriff auf die angefragten Daten autorisiert ist. Die Lösung ist ein föderiertes IAM-System, das auf etablierten Industriestandards aufbaut 28:
Authentifizierung („Wer bist du?“): Durch den Einsatz von Protokollen wie SAML 2.0 oder OpenID Connect (OIDC) wird ein domänenübergreifendes Single Sign-On (SSO) ermöglicht. Ein Nutzer meldet sich an seinem lokalen System an und kann dann, vermittelt durch einen Trust zwischen den Identitätsprovidern (IdPs) der Länder oder über einen zentralen Bundes-IdP, auf Ressourcen in anderen Ländern zugreifen, ohne sich erneut anmelden zu müssen.
Provisionierung („Wer darf was?“): Der Standard SCIM (System for Cross-Domain Identity Management) ermöglicht die automatisierte Synchronisation von Benutzer- und Gruppeninformationen, einschließlich ihrer Rollen und Berechtigungen, zwischen den Systemen.31 Ändert sich die Rolle eines Mitarbeiters in Bayern, kann diese Information automatisch an die Systeme der anderen Länder übermittelt werden, um seine Berechtigungen dort anzupassen.
Autorisierung im Gateway: Die zentrale Gateway-Schicht wird zum primären Policy Enforcement Point. Sie prüft bei jeder eingehenden Anfrage die mitgesendeten digitalen Signaturen oder Tokens (z.B. JWTs), validiert die Berechtigungen des anfragenden Nutzers und leitet nur autorisierte Sub-Anfragen an die jeweiligen Landesinstanzen weiter.

4.2 Etablierung einer föderierten Data Governance

Technische Interoperabilität durch standardisierte APIs ist nur die halbe Miete. Damit die Systeme nicht nur miteinander reden können, sondern sich auch verstehen, ist semantische Interoperabilität erforderlich. Dies erfordert einen kooperativen Governance-Prozess, der im Data-Mesh-Paradigma als „Federated Computational Governance“ bezeichnet wird.13 Ein solches föderales Governance-Gremium, beispielsweise ein „KI-Föderationsrat“ als Unterausschuss des IT-Planungsrats, hätte folgende Kernaufgaben:
Standardisierung der Ontologie: Gemeinsame Definition von Knoten-Labeln, Eigenschaften und Kanten-Typen für Verwaltungsobjekte von bundesweiter Relevanz. Beispielsweise muss eine einheitliche Definition für Entitäten wie :Unternehmen, :Standort oder :Genehmigungsbescheid existieren, damit Abfragen über Ländergrenzen hinweg konsistente Ergebnisse liefern.
Verwaltung des URN-Schemas: Pflege und Erweiterung der gültigen Namespaces, wie der Länderkürzel, Fachdomänen und Objekttypen.
API-Standardisierung: Verbindliche Festlegung des GraphQL-Schemas, das jede Landesinstanz als ihre öffentliche Schnittstelle (Subgraph) bereitstellen muss.
Datenqualitäts- und Lebenszyklus-Richtlinien: Festlegung von Mindeststandards für die Datenpflege sowie gemeinsamer Regeln für Aufbewahrungs- und Löschfristen, um den gesamten Datenlebenszyklus DSGVO-konform zu gestalten.35
Die Entscheidung für eine föderierte IT-Architektur ist somit implizit die Entscheidung für die Schaffung eines neuen, dauerhaften, kooperativen Governance-Prozesses. Die technischen Herausforderungen sind in Wirklichkeit organisatorische Abstimmungsprozesse auf Bundesebene.

4.3 Gewährleistung transaktionaler Konsistenz: Das Saga-Pattern

Während Lesezugriffe über die Föderationsschicht relativ einfach zu realisieren sind, stellen schreibende Geschäftsprozesse, die Daten in mehreren Ländern konsistent ändern müssen (z.B. die Ummeldung eines Unternehmenssitzes von Bayern nach NRW), eine weitaus größere Herausforderung dar.
Das Problem mit klassischen Transaktionen: Ein klassischer verteilter Transaktionsmechanismus wie der Two-Phase Commit (2PC) ist für moderne, lose gekoppelte Microservice-Architekturen ungeeignet. Er erfordert, dass alle beteiligten Systeme während der gesamten Transaktion Ressourcen sperren (sog. "Blocking"), was die Verfügbarkeit und Skalierbarkeit des Gesamtsystems massiv einschränkt. Der Ausfall des zentralen Koordinators kann das gesamte System in einem inkonsistenten, blockierten Zustand hinterlassen.37
Die Lösung: Das Saga-Pattern: Das Saga-Pattern bietet einen alternativen Ansatz zur Gewährleistung von „eventual consistency“. Eine Saga zerlegt einen globalen Geschäftsprozess in eine Sequenz von lokalen, unabhängigen Transaktionen. Jeder Schritt wird in seinem jeweiligen Dienst ausgeführt und committet. Wenn ein Schritt fehlschlägt, werden die vorherigen, bereits erfolgreich abgeschlossenen Schritte durch explizit definierte „kompensierende Transaktionen“ rückgängig gemacht.41
Orchestrierung vs. Choreographie: Es gibt zwei Modelle zur Koordination einer Saga. Bei der Choreographie publiziert jeder Dienst nach Abschluss seiner lokalen Transaktion ein Event, auf das der nächste Dienst im Prozess reagiert. Dies führt zu einer sehr losen Kopplung, macht den Gesamtprozess aber schwer nachvollziehbar und auditierbar.42 Bei der Orchestrierung gibt es einen zentralen „Saga Orchestrator“, der den gesamten Prozess steuert, Befehle an die einzelnen Dienste sendet und im Fehlerfall die Kompensationen koordiniert. Dieses Modell bietet eine klare Kontrolle, eine zentrale Sicht auf den Prozessstatus und eine vereinfachte Auditierbarkeit.46
Für den Anwendungsfall in der öffentlichen Verwaltung, wo Nachvollziehbarkeit und Revisionssicherheit oberste Priorität haben, ist das Orchestrierungs-Modell klar zu bevorzugen. Der Saga Orchestrator kann logisch in der zentralen Föderations-Gateway-Schicht angesiedelt werden.

Teil V: Strategische Empfehlungen und Implementierungs-Roadmap

Basierend auf der vorangegangenen Analyse lassen sich eine klare Architekturempfehlung, ein pragmatisches Vorgehensmodell und eine strategische Einordnung in die bestehende IT-Landschaft der deutschen Verwaltung ableiten.

5.1 Vergleichende Bewertung und finale Architekturempfehlung

Die empfohlene Architektur ist eine Gateway-basierte Föderationsarchitektur, die auf GraphQL Federation aufbaut. Dieses Modell bietet den besten Kompromiss aus föderaler Autonomie, zentraler Kontrolle, Sicherheit, Auditierbarkeit und technischer Skalierbarkeit für den öffentlichen Sektor.
Begründung: Der zentrale Gateway schafft einen klaren und kontrollierbaren Punkt für die Durchsetzung von Sicherheits- und Governance-Richtlinien (Policy Enforcement Point). Er vereinfacht das Monitoring, die Protokollierung und die Fehlersuche im Vergleich zu einem rein dezentralen Peer-to-Peer-Ansatz erheblich. Die Verwendung von GraphQL als API-Technologie bietet eine flexible, stark typisierte und zukunftssichere Schnittstellenschicht, die die Komplexität der darunterliegenden 16 heterogenen RAG-Instanzen (Subgraphs) für den Endanwender und die Client-Anwendungen vollständig verbirgt.

5.2 Phasenmodell zur Implementierung (Agiler Ansatz)

Eine Implementierung dieser Größenordnung sollte agil und phasenweise erfolgen, um frühzeitig Erfahrungen zu sammeln und Risiken zu minimieren.
Phase 1 (6 Monate): Fundament und Standardisierung:
Einsetzung des föderalen Governance-Gremiums (z.B. „KI-Föderationsrat“).
Verabschiedung des finalen URN-Schemas und der Kern-Ontologie für bundesweit relevante Objekte.
Entwicklung und Verabschiedung des Standard-API-Vertrags (Basis-GraphQL-Schema) für alle Landesinstanzen.
Phase 2 (9 Monate): Bilateraler Pilot:
Auswahl von zwei bis drei Pilot-Bundesländern mit einem klar definierten, länderübergreifenden Anwendungsfall.
Aufbau eines Proof-of-Concept des Föderations-Gateways.
Implementierung der standardisierten APIs in den Pilot-Ländern und Test der ersten länderübergreifenden Lese-Abfragen.
Phase 3 (12 Monate): Erweiterter Pilot und Transaktionen:
Anbindung von drei bis fünf weiteren Ländern.
Implementierung und Test des Saga-Orchestrators für erste schreibende, länderübergreifende Prozesse.
Aufbau und Integration des föderierten Identitäts- und Zugriffsmanagements (IAM).
Phase 4 (fortlaufend): Bundesweiter Rollout:
Sukzessive Anbindung der verbleibenden Länder an das föderierte System.
Überführung des Gateways und der angebundenen Instanzen in den produktiven Betrieb.
Kontinuierliche Weiterentwicklung der Ontologie und der Föderationsdienste durch das etablierte Governance-Gremium.

5.3 Integration in die "Deutsche Verwaltungscloud-Strategie" (DVS) und den "Deutschland-Stack"

Das hier entworfene föderierte RAG-Netzwerk ist keine Konkurrenz zu bestehenden nationalen IT-Strategien, sondern deren logische und wertschöpfende Ergänzung. Es sollte als eine intelligente, föderale Anwendungsschicht (PaaS/SaaS-Ebene) verstanden werden, die auf der souveränen Infrastruktur (IaaS-Ebene) des „Deutschland-Stacks“ und der „Deutschen Verwaltungscloud-Strategie“ aufsetzt.2
Daraus ergeben sich erhebliche Synergien:
Souveränes Hosting: Die 16 Landesinstanzen und der zentrale Föderations-Gateway können als Container-Anwendungen in der DVS betrieben werden. Dies gewährleistet maximale digitale Souveränität, da alle Komponenten auf staatlich kontrollierter Infrastruktur laufen.
Nutzung zentraler Dienste: Das föderierte IAM kann an die zentralen Identitätsdienste des Deutschland-Stacks anknüpfen, um eine einheitliche Authentifizierung für Verwaltungsmitarbeiter zu schaffen.
Verzahnung mit Registermodernisierung: Das entwickelte URN-Schema kann als Basis für die eindeutige, quellenübergreifende Adressierung von Objekten (Bürger, Unternehmen) im Rahmen der Registermodernisierung dienen und so die Verknüpfung von Registerdaten erleichtern.
Strategisches Fazit: Dieses Projekt ist mehr als nur eine technische Lösung für eine spezifische Anfrage. Es stellt einen konkreten, wertschöpfenden Anwendungsfall für die nationale Cloud-Strategie dar. Es kann deren Nutzen demonstrieren, indem es aus reiner Infrastruktur eine intelligente, vernetzte und föderal organisierte Wissensplattform für die gesamte deutsche Verwaltung macht und somit einen entscheidenden Beitrag zur Sicherung der staatlichen Handlungsfähigkeit im digitalen Zeitalter leistet.
Referenzen
RAG-Graph LLM für BImSchG-Überwachung
Visual Processing Backbone (VPB) - KI-Integration in Brandenburgs Verwaltung
VERITAS-Einführung: Mensch-zentrierte Strategie
Digitale Souveränität – Einfach erklärt - Deutsche Telekom, Zugriff am Oktober 11, 2025, https://www.telekom.com/de/konzern/details/digitale-souveraenitaet-einfach-erklaert-1088912
Covina Architektur
Polyglot Persistence: A Comprehensive Guide for Database Developers Transitioning to Microservices Architecture, Zugriff am September 27, 2025, https://thedeveloperspace.com/polyglot-persistence/
Polyglot Persistence - Martin Fowler, Zugriff am September 27, 2025, https://martinfowler.com/bliki/PolyglotPersistence.html
What is Polyglot Persistence? - James Serra's Blog, Zugriff am September 27, 2025, https://www.jamesserra.com/archive/2015/07/what-is-polyglot-persistence/
The Pros and Cons of Polyglot Persistence, Zugriff am September 27, 2025, https://www.opensourceforu.com/2015/08/the-pros-and-cons-of-polyglot-persistence/
Datensouveränität für die öffentliche Verwaltung: STACKIT unterstützt die Deutsche Verwaltungscloud-Strategie - Schwarz Digits, Zugriff am Oktober 11, 2025, https://schwarz-digits.de/presse/archiv/2024/datensouveraenitaet-fuer-die-oeffentliche-verwaltung-stackit-unterstuetzt-die-deutsche-verwaltungscloud-strategie
Datenpolitik - CIO.Bund.de, Zugriff am Oktober 11, 2025, https://www.cio.bund.de/Webs/CIO/DE/digitale-loesungen/datenpolitik/datenpolitik-node.html
PD-Impulse Datensouveränität - PD - Berater der öffentlichen Hand, Zugriff am Oktober 11, 2025, https://www.pd-g.de/pd-impulse-reihe/pd-impulse-datensouveraenitaet
Federated Learning and Data Mesh: how it enhances data architecture - www.apheris.com, Zugriff am Oktober 11, 2025, https://www.apheris.com/resources/blog/federated-learning-and-data-mesh
What is a Data Mesh? - Data Mesh Architecture Explained - AWS - Updated 2025, Zugriff am Oktober 11, 2025, https://aws.amazon.com/what-is/data-mesh/
Complete Guide to Data Federation: All You Need to Know, Zugriff am Oktober 11, 2025, https://hydrolix.io/glossary/data-federation/
System Design - Database Federation - Tutorials Point, Zugriff am Oktober 11, 2025, https://www.tutorialspoint.com/system_analysis_and_design/system_design_database_federation.htm
Data Federation: What It Is and Why Your Business Needs It ..., Zugriff am Oktober 11, 2025, https://www.gooddata.com/blog/data-federation-what-it-is-and-why-your-business-needs-it/
Database Federation - System Design - GeeksforGeeks, Zugriff am Oktober 11, 2025, https://www.geeksforgeeks.org/system-design/database-federation-system-design/
Why Data Mesh is a Must for Federated Data Management - K2view, Zugriff am Oktober 11, 2025, https://www.k2view.com/blog/federated-data-management/
Understanding UUIDs: A Backend Engineer's Guide for Junior Developers, Zugriff am September 25, 2025, https://dev.to/usooldatascience/understanding-uuids-a-backend-engineers-guide-for-junior-developers-5075
generate unique sequential IDs in microservices architecture - Software Engineering Stack Exchange, Zugriff am September 25, 2025, https://softwareengineering.stackexchange.com/questions/361491/generate-unique-sequential-ids-in-microservices-architecture
RFC 2141 - URN Syntax - IETF Datatracker, Zugriff am Oktober 11, 2025, https://datatracker.ietf.org/doc/html/rfc2141
Uniform Resource Identifier - Wikipedia, Zugriff am Oktober 11, 2025, https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
Aktenzeichen | Bedeutung & Erklärung | Legal Lexikon, Zugriff am September 25, 2025, https://www.mtrlegal.com/wiki/aktenzeichen/
Aktenzeichen (Deutschland) - Wikipedia, Zugriff am September 25, 2025, https://de.wikipedia.org/wiki/Aktenzeichen_(Deutschland)
Bundesarchiv - Hinweise für die Aufstellung von Aktenplänen, Zugriff am September 25, 2025, https://www.bundesarchiv.de/assets/bundesarchiv/de/Downloads/Erklaerungen/beratungsangebote-aktenplan-hinweise-fuer-die-aufstellung-von-aktenplaenen-juni-2022.pdf
Universally unique identifier - Wikipedia, Zugriff am September 25, 2025, https://en.wikipedia.org/wiki/Universally_unique_identifier
What Is Federated Identity Management | Securends, Zugriff am Oktober 11, 2025, https://www.securends.com/blog/federated-identity-management/
Identity federation in AWS, Zugriff am Oktober 11, 2025, https://aws.amazon.com/identity/federation/
How Does Federated Identity Work? Benefits and Tips - Rippling, Zugriff am Oktober 11, 2025, https://www.rippling.com/blog/federated-identity
Best System for Cross-Domain Identity Management (SCIM) Reviews 2025 - Gartner, Zugriff am Oktober 11, 2025, https://www.gartner.com/reviews/market/system-for-cross-domain-identity-management-scim
What is System for Cross-Domain Identity Management (SCIM) ?- Security Wiki, Zugriff am Oktober 11, 2025, https://doubleoctopus.com/security-wiki/protocol/system-for-cross-domain-identity-management/
What is SCIM? A Guide to Cross-Domain Identity Management - LoginRadius, Zugriff am Oktober 11, 2025, https://www.loginradius.com/blog/identity/what-is-scim
Data Mesh 101: Why Federated Data Governance Is the Secret Sauce of Data Innovation, Zugriff am Oktober 11, 2025, https://www.mesh-ai.com/case-studies/data-mesh-101-why-federated-data-governance-is-the-secret-sauce-of-data-innovation
Datenmanagement für die öffentliche Verwaltung - SAS, Zugriff am September 25, 2025, https://www.sas.com/de_ch/industry/government/technology/data-management.html
Der Lebenszyklus von Daten und seine Bedeutung aus rechtlicher Sicht - KPMG-Law, Zugriff am September 25, 2025, https://kpmg-law.de/der-lebenszyklus-von-daten-und-seine-bedeutung-aus-rechtlicher-sicht/
Why 2-Phase Commit Fails in Microservices — And How the Saga Pattern Saves the Day, Zugriff am September 27, 2025, https://dev.to/akshay161099/why-2-phase-commit-fails-in-microservices-and-how-the-saga-pattern-saves-the-day-3f9p
Why is 2-phase commit not suitable for a microservices architecture? - Codemia.io, Zugriff am September 27, 2025, https://codemia.io/knowledge-hub/path/why_is_2-phase_commit_not_suitable_for_a_microservices_architecture
Why is 2-phase commit not suitable for a microservices architecture? - Stack Overflow, Zugriff am September 27, 2025, https://stackoverflow.com/questions/55249656/why-is-2-phase-commit-not-suitable-for-a-microservices-architecture
Two-Phase Commit Protocol Explained - Endgrate, Zugriff am September 27, 2025, https://endgrate.com/blog/two-phase-commit-protocol-explained
Saga Design Pattern - Azure Architecture Center | Microsoft Learn, Zugriff am September 27, 2025, https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
Pattern: Saga - Microservices.io, Zugriff am September 27, 2025, https://microservices.io/patterns/data/saga.html
The Saga Design Pattern: Coordinating Long-Running Transactions in Distributed Systems, Zugriff am September 25, 2025, https://medium.com/@CodeWithTech/the-saga-design-pattern-coordinating-long-running-transactions-in-distributed-systems-edbc9b9a9116
Compensating transaction - Wikipedia, Zugriff am September 27, 2025, https://en.wikipedia.org/wiki/Compensating_transaction
What is the difference between Orchestration and Choreography in Microservices architecture? - YouTube, Zugriff am September 27, 2025, https://www.youtube.com/watch?v=3dCdXU7jy0s
Coordinating distributed systems with the Saga Pattern on AWS | willdady.com, Zugriff am September 27, 2025, https://willdady.com/coordinating-distributed-systems-with-the-saga-pattern-on-aws
Saga Pattern in Microservices: Orchestration vs Choreography - DEV Community, Zugriff am September 27, 2025, https://dev.to/rock_win_c053fa5fb2399067/saga-pattern-in-microservices-orchestration-vs-choreography-mml
Saga orchestration pattern - AWS Prescriptive Guidance, Zugriff am September 27, 2025, https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html
berücksingt