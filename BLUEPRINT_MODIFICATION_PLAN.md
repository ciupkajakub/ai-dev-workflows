# Plan uproszczenia blueprintu

Status: propozycja do akceptacji. Data: 2026-10-07. Punkt odniesienia: blueprint 4.4.0, commit `b692c40`. Ten dokument nie zmienia działania workflow ani instalacji w aplikacjach.

## Cel i diagnoza

Zachowujemy proces: potrzeba biznesowa → rozpoznanie kodu i wyjaśnienie decyzji → zrozumiała propozycja → jedna akceptacja → implementacja, niezależna weryfikacja i naprawy → PR z zakończonymi wymaganymi sprawdzeniami → odbiór przez człowieka. Koordynator odpowiada za doprowadzenie zatwierdzonego zakresu do tej granicy. Merge i deployment wymagają osobnej zgody.

Obecny problem polega na powtarzaniu zasad między dokumentami oraz na rozbieżności między kompletnym raportem a rzeczywiście sprawdzonym zachowaniem. Kolejne instrukcje poprawiały wybrane decyzje agentów, ale nie dały jeszcze dowodu skuteczności całej dostawy.

Sam blueprint ma 852 linie i około 7325 słów. README, blueprint i pliki Markdown pod `skills/` mają łącznie około 12 956 słów. Pierwsza wersja schema 4 miała około 4673 słów w blueprintcie, więc wzrost wynosi około 57%. To pomiar tekstu przez podział po białych znakach, nie pomiar kontekstu faktycznie przeczytanego przez agenta. Skrócenie plików będzie pomocne, ale o wyniku zdecydują wykonania workflow.

## Co przeczytano i czego nie potwierdzono

Analiza obejmuje obecny blueprint, README, pięć wejściowych skilli, wspólne reguły, instrukcje review i publikacji, checker publikacji, mechanizm sprawdzania pakietu oraz zachowane raporty i materiały prób od przygotowania propozycji do wersji 4.4. Historia Git pozwala prześledzić narastanie instrukcji.

Źródła zewnętrzne odczytano z gałęzi `main` wskazanych repozytoriów. Przeczytano cały skill show-me oraz wybrane instrukcje związane z naszym procesem z pozostałych dwóch kolekcji. To analiza celowego przekroju, nie audyt każdego skilla. Nie wykonano tych zewnętrznych workflow ani nowej pełnej próby naszego. Popularność i deklaracje autorów nie są porównawczym dowodem skuteczności.

| Źródło | Wniosek dla nas | Granica zastosowania |
| --- | --- | --- |
| [Humanlayer show-me](https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md) | Dobierać najmniejszy widok, który wyjaśnia zmianę: wywołanie, różnicę interfejsu lub przepływ. | To pomoc w prezentacji. Nie opisuje pełnej dostawy ani kontroli dowodów. |
| [Pstack poteto-mode](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md) i [feature](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/feature.md) | Koordynator wybiera procedurę potrzebną na danym etapie i odpowiada za zakończenie pracy. | Pstack też jest rozbudowany. Nie kopiujemy jego przypisanych modeli, narzędzi ani szerszych uprawnień. |
| [Pstack encode lessons in structure](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-encode-lessons-in-structure/SKILL.md) | Powtarzalne, jednoznaczne warunki przenosić do mechanizmu sprawdzającego; osąd pozostawić jawnie człowiekowi lub agentowi. | Dodatkowe pole JSON nie sprawdza prawdziwości obserwacji. |
| [Pstack eval](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md) | Ustalać kryteria przed próbą, nie ujawniać oczekiwanych błędów wykonawcy i czytać przebieg wykonania. | Liczbę prób dobieramy do kosztu i ryzyka. Nie wprowadzamy stałego zestawu modeli. |
| [Matt Pocock writing-for-agents](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md) | Każda instrukcja ma jedno miejsce; odsyłacz mówi, kiedy czytać wskazany materiał. | Rozdzielanie plików musi zmniejszać pracę czytelnika. Sam wzrost liczby małych plików niczego nie rozwiązuje. |
| [Matt Pocock implement](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md), [to-spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md) i [code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) | Oddzielić przygotowanie specyfikacji, wykonanie i ocenę względem wymagań. | Krótki skill korzysta z innych procedur. Nie oznacza to równie krótkiego całego procesu. |

Źródła wymagają krytycznej selekcji. Przykładowo [pstack babysit](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/babysit.md) zawiera heurystykę wiążącą awarię poza zmienianym kodem ze starą bazą. Nasze próby pokazują, dlaczego samo położenie błędu poza diffem nie wystarcza do odrzucenia związku ze zmianą.

## Wnioski z iteracji

| Zachowany materiał | Co pokazał | Ogólna zmiana procesu |
| --- | --- | --- |
| [Gotowość propozycji](tests/proposal_readiness_case.md) i [kolejny review](tests/proposal_review_followup.md) | Propozycja mogła opisać walidację bez wykazania, że uruchamia ją rzeczywisty klient. Pojawiało się też rozszerzanie zakresu. | Przygotowanie zaczyna od wymagań i rzeczywistego przebiegu operacji przez granice komponentów. |
| [Próba uproszczenia](tests/proposal_simplification_case.md) i [4.2](tests/workflow_42_case.md) | Krótsze instrukcje nie gwarantowały krótszych artefaktów ani kompletności planu. Ograniczone próby rozmowy nie dowodziły dostawy. | Mierzyć osobno koszt czytania, jakość propozycji i wynik wykonania. |
| [4.2.1](tests/workflow_421_delivery_case.md) i [4.3](tests/workflow_43_case.md) | Niezależne sprawdzenie znajdowało pominięte ścieżki i problemy ze stanem, ale sam review nie zamykał napraw. | Rozdzielić wykonawcę i weryfikatora; wynik negatywny automatycznie wraca do naprawy w zatwierdzonym zakresie. |
| [4.3.1](tests/workflow_431_case.md) | Zielone wyniki nie obejmowały właściwego wyzwalacza, pełnego zbioru plików ani potwierdzonego dalszego monitorowania. | Sprawdzać zakres wykonanej obserwacji i faktyczny mechanizm kontynuacji. |
| [4.3.2](tests/workflow_432_case.md) | Wybór gałęzi/PR, stan istniejącego PR, prezentacja interfejsów i zapis postępu wymagały doprecyzowania. | Związać zgodę z rozpoznanym celem i operacją; prezentację interfejsów wykonywać już przy akceptacji. |
| [4.4](tests/workflow_44_case.md) | Raport pozostawał zielony mimo przyznanego braku dowodu i odrzuconego znanego błędu. Checker schema 2 wykrywa niekompletne rekordy, jeśli otrzyma pełny oczekiwany zbiór. | Ocena pokrycia musi wychodzić od wymagań. Checker pozostaje kontrolą zapisu, nie dowodem zachowania. |

Historyczne przypadki zostają materiałem testowym. W instrukcjach wykonawczych nie dodajemy nazw metod, etykiet CI, numerów przypadków ani osobnych zakazów odpowiadających tym incydentom.

## Docelowy podział instrukcji

Zostają obecne komendy i dokumenty aplikacji. Nie wprowadzamy nowego orchestratora, nowych komend użytkownika ani dodatkowego rejestru stanu.

| Miejsce | Jedyna odpowiedzialność |
| --- | --- |
| `README.md` | Wejście dla człowieka: cel, przebieg, dostępne komendy, miejsca przechowywania informacji. |
| `feature_execution_blueprint.md` | Krótki wspólny kontrakt: zakres zgody, role, przejścia, źródła prawdy i definicja zakończenia. |
| `skills/entry-rules.md` | Wybór repozytorium, pakietu i istniejącej pracy. Odsyła do kontraktu bez jego przepisywania. |
| `workflow-prepare/SKILL.md` | Rozpoznanie, pytania o rzeczywiste decyzje, plan i prezentacja do akceptacji. |
| `workflow-deliver/SKILL.md` | Koordynowanie wykonania, niezależnej weryfikacji, napraw i przekazania PR. |
| `workflow-feedback/SKILL.md` | Ocena informacji zwrotnej: naprawa w ramach zgody albo zmiana wymagająca nowej decyzji. Dalej używa tej samej procedury dostawy. |
| `workflow-resume/SKILL.md` | Odtworzenie aktualnego stanu i wejście we właściwy etap. Nie powiela całego wykonania. |
| `workflow-setup/SKILL.md` i `skills/install.md` | Instalacja, aktualizacja, kompatybilność i identyfikacja pakietu. |
| Referencje pod odpowiednim skillem | Szczegóły review, dowodów i szablonów czytane w chwili użycia. |

Każdy skill określa wejście, działania, warunek zakończenia i następny etap. Zasady potrzebne na każdej ścieżce znajdują się w obowiązkowym kontrakcie. Odsyłacze do procedur warunkowych podają moment ich użycia. Istniejące `FEATURE`, `IMPLEMENTATION`, `PROGRESS`, `WORK_INDEX` i backlog zachowują swoje role.

Proponowany cel redakcyjny to około 1200–1800 słów wspólnego kontraktu i zmniejszenie łącznego tekstu aktywnych instrukcji o około 40%. To cel orientacyjny, nie warunek automatycznego testu. Dodatkowo mierzymy tekst wymagany na wejściu do każdego etapu, łącznie z obowiązkowymi odsyłaczami. Historia prób i przykłady nie są częścią obowiązkowej lektury podczas dostawy.

## Zmiany zachowania

### 1. Jedna podstawa propozycji i jej weryfikacji

`FEATURE` pozostaje źródłem oczekiwanego zachowania i decyzji. `IMPLEMENTATION` opisuje sposób zmiany i sprawdzenia. Akceptacja dotyczy wskazanych rewizji, repozytorium, celu pracy i zakresu operacji. Zmiana celu lub zakresu uruchamia ponowną ocenę zgody, a zwykła naprawa w tym zakresie kontynuuje dostawę.

Przygotowanie śledzi rzeczywistą operację przez wywołującego, granice interfejsów, wynik i jego konsumenta. Bada te przejścia oraz zachowania zastępowanej ścieżki, których dotyka zmiana. Nie wymaga enumeracji wszystkich możliwych przypadków całej aplikacji. Pytania do użytkownika dotyczą brakujących decyzji biznesowych; fakty o kodzie ustala agent.

### 2. Interfejsy widoczne przy akceptacji

Podsumowanie pokazuje rezultat, istotne decyzje, zmieniane odpowiedzialności oraz wejścia i wyniki przed/po. Konkretne sygnatury lub przykład wywołania pojawiają się wtedy, gdy wyjaśniają kontrakt. Diagram służy do pokazania zależności lub zmian stanu. Prosta zmiana nie musi dostać diagramu.

Użytkownik powinien z tej prezentacji rozumieć, co zatwierdza, bez czytania dziennika agenta. Treść powstaje z tej samej propozycji, którą otrzyma wykonawca. Nie utrzymujemy osobnego opisu rozwiązania tylko na potrzeby prezentacji.

### 3. Weryfikacja zaczyna od obietnic

Niezależny weryfikator otrzymuje pierwotne wymagania, zatwierdzone decyzje, ustaloną rewizję i dostęp do aplikacji. Najpierw ustala zachowania wymagające dowodu, potem ocenia implementację i wyniki. W istniejącej notatce review wiąże wymaganie z wyzwalaczem, rzeczywistą ścieżką wykonania, obserwacją i dowodem.

Poziom sprawdzenia wynika z obietnicy. Test komponentu wystarcza dla jego izolowanego kontraktu; zachowanie zależne od połączenia komponentów wymaga dowodu obejmującego to połączenie. Znane niepowodzenie pozostaje otwarte do naprawy lub uzasadnionego odrzucenia na podstawie porównania zakresu i zachowania. Niepowodzenie weryfikacji kieruje do naprawy w ramach udzielonej zgody.

Nie tworzymy drugiego katalogu wymagań. Identyfikatory w dowodach wskazują wymagania w `FEATURE` i sprawdzenia w planie. Podział złożonego wymagania na obserwowalne części ma służyć ocenie jego pokrycia, nie generowaniu kolejnej dokumentacji.

### 4. Checker ma ograniczoną, uczciwie opisaną rolę

Zachowujemy kontrole tożsamości pracy, rewizji, obecności wymaganych rekordów i dostępności artefaktów. Nie usuwamy zabezpieczeń schema 2 tylko dla skrócenia dokumentacji. Jednocześnie wprost zapisujemy, że checker nie ocenia kompletności listy podanej przez wywołującego ani prawdziwości dowodu.

Koordynator porównuje zakres review z zatwierdzonymi wymaganiami i znanymi wynikami, zamiast bezkrytycznie przyjmować listę z receipt. Nie budujemy parsera rozumiejącego wymagania ani systemu imitującego uwierzytelnienie niezależnego review przez dodatkowe pola JSON. Mechaniczne warunki testujemy skryptem, jakość oceny sprawdzamy próbami agentów.

### 5. Aktualny postęp bez przepisywania historii dowodów

Porządkujemy istniejącą możliwość ponownego użycia dowodów po zmianie metadanych. Dowód zachowuje pierwotną rewizję wykonania testu. Po kolejnym commicie weryfikator sprawdza różnicę i jawnie zapisuje podstawę zastosowania wcześniejszego wyniku do nowej rewizji. Zmiana kodu, testów, konfiguracji lub zależności wymaga ponownej oceny wpływu i właściwych sprawdzeń.

Aktualizacja stanu po publikacji i po wyniku CI musi być zapisana oraz commitowana. Nie cofamy zakończonego etapu tylko dlatego, że zapisano jego rezultat. Rozdzielamy rewizję poddaną wymaganym sprawdzeniom od późniejszego commita stanu workflow, pokazując obie w przekazaniu. Jeżeli projekt wymaga CI na każdym nowym HEAD, workflow czeka także na ten wynik. Nie deklarujemy wtedy zakończenia przed jego otrzymaniem.

W pierwszej kolejności upraszczamy tę procedurę bez zmiany formatu receipt. Dopiero test ujawniający ograniczenie obecnego formatu uzasadnia minimalną zmianę schematu. Nie wprowadzamy nowego systemu identyfikatorów ani szerokiego wyłączenia plików ze sprawdzania.

## Kolejność wykonania po akceptacji

| Etap | Zmiana i granica commita | Sprawdzenie |
| --- | --- | --- |
| 1. Ustalenie punktu odniesienia | Zapisać kryteria porównania i mapę właścicieli reguł. Wybrać różne klasy zadań oraz zachować obecne materiały regresji. | Każda obowiązująca gwarancja ma docelowego właściciela; kryteria ustalone przed kandydatem. |
| 2. Podział dokumentacji | Skrócić kontrakt, przenieść procedury do skilli i referencji, usunąć duplikaty, poprawić README. Osobny commit bez zmiany semantyki zgód. | Walidator dokumentów, kompletność pakietu, istniejące testy, pomiar tekstu czytanego na etap. |
| 3. Przygotowanie i prezentacja | Ujednolicić podstawę wymagań, przepływu i podsumowania interfejsów. | Odtworzenie zachowanych błędnych propozycji oraz nowa propozycja bez znajomości oczekiwanych usterek. |
| 4. Dostawa i dowody | Połączyć review, naprawy, publikację i zapis postępu w jedną spójną procedurę; doprecyzować ponowne użycie dowodów. | Istniejące testy checkera oraz testy rzeczywiście zmienionej logiki. Osobno próba odtworzenia pracy po przerwaniu. |
| 5. Porównanie pełnych wykonań | Uruchomić baseline i kandydata na tych samych zadaniach, w oddzielnych środowiskach. Zachować przebiegi, wyniki i koszty. | Ocena według wcześniej ustalonych kryteriów; brak podpowiedzi o oczekiwanych usterkach w promptach wykonawcy. |
| 6. Decyzja o wydaniu | Na podstawie wyników przyjąć kandydata lub poprawić wykazaną słabość. Dopiero potem aktualizować wersję i przygotować instrukcję migracji pakietu. | Sprawdzenie rzeczywistego pakietu, jawne ograniczenia i brak regresji zakresu zgody. Instalacje w aplikacjach pozostają osobnym działaniem. |

Każdy etap ma mały commit obejmujący wyłącznie jego zmiany. Etap 2 nie może sam stanowić dowodu, że poprawiono działanie agentów.

## Jak ocenimy rezultat

Potrzebne są co najmniej różne klasy problemów: prosta zmiana w jednym komponencie, operacja przekraczająca granice komponentów oraz przerwane wykonanie z istniejącym stanem i wynikiem zewnętrznym. Co najmniej jedno zadanie pochodzi z innej domeny niż dotychczasowy checkout. Część próbek ujawniamy dopiero podczas oceny kandydata, aby instrukcje nie zostały dopasowane do znanych usterek. Uwzględniamy poprawne wykonanie, żeby workflow nie wygrywał przez blokowanie wszystkiego.

Porównujemy:

- zgodność propozycji z potrzebą i zakres pytań wymagających odpowiedzi użytkownika;
- czytelność decyzji i zmian interfejsów przed akceptacją;
- faktyczne pokrycie obiecanych zachowań i reakcję na niepowodzenia;
- dotarcie do uzgodnionej granicy dostawy bez ponownego proszenia o tę samą zgodę;
- poprawność celu publikacji, aktualność zapisu i możliwość wznowienia;
- objętość instrukcji, dokumentów i rozmowy oraz koszt wykonania, gdy dostępny.

Kandydat nie przechodzi oceny, jeśli pomija istotne wymaganie, deklaruje nieuzyskany dowód albo przekracza zgodę. Wyniki podajemy dla poszczególnych prób, bez ukrywania poważnego błędu za średnią. Mała liczba udanych prób oznacza ograniczony dowód, nie gwarancję niezawodności. Niedostępnego CI lub rzeczywistej publikacji nie zastępujemy symulacją opisaną jako pełna dostawa.

Akceptacja tego planu pozwala przebudować i zweryfikować źródła workflow w tym repozytorium. Nie oznacza naprawy aplikacyjnego B119, aktualizacji cudzych instalacji ani zgody na nieokreślone zewnętrzne publikacje czy płatne eksperymenty. Dla pełnej próby wymagającej takich operacji trzeba wskazać środowisko i zakres uprawnień.
