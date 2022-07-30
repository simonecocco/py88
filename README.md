# **py88** - _Un piccolo emulatore per il linguaggio assemblativo 8088_
## **Il progetto**
Il progetto consiste nella progettazione e nella successiva realizzazione di un emulatore capace di leggere i file .s contenenti un programma in linguaggio assemblativo per 8088.

## **Directory tree**
```
py88
|-main.py
|-file_checker.py
|-py88.py
|-executer.py
|-exceptions.py
|-divide_file.py
|-register.py
|-stack.py
|-instruction.py
|-variable.py
|-test.s
'-README.md
```
* `main.py`: Il file main.py si occupa di inizializzare l'ambiente ricavando le variabili,
validando il file e avviando l'esecuzione;
* `registers.py`: La classe che gestisce tutta la parte dei registri;
Consente di memorizzare un valore tramite registers[x]=y e di leggere il registro y = registers[x].
Ogni registro è unsigned int da 2 byte, supporta anche i registri HL da 1 byte (unsigned char);
* `file_checker.py`: valida il file. Si occupa di controllare se il file esiste, se non è una directory e se il file è leggibile;
* `exceptions.py`: il file che contiene le varie classi di eccezioni;
* `py88.py`: è la classe che si occupa di interpretare le istruzioni;
* `stack.py`: è la classe che si occupa di emulare il comportamento dello stack memorizzando interi a 2byte (indirizzi e dati);
* `test.s`: file di test scritto in 8088
* `instruction.py`: la classe Instruction contiene l'istruzione ed i suoi operandi, in modo da poterli richiamare al bisogno;
* `variable.py`: la classe Var contiene il nome, la dimensione del dato, in modo da poterli richiamare al bisogno;
* `divide_file.py`: si occupa di fare il parse del programma dividendo sezione text, bss, data e le costanti;
* `executer.py`: la classe core esegue le istruzioni andando a modificare stack, registri e i valori in memoria
## **Come utilizzare py88**
> **richiede python 3.10**

Per usare py88 è sufficiente richiamare python3 passando come argomento il file main.py.
```Shell
python3 py88/main.py test.s
```
> se si volesse eseguire il debug al codice è sufficiente aggiungere l'opzione `-d` dopo il file .s
## **Istruzioni**
> op, op1, op2 sono operandi generici. Essi possono essere referenze a
> dati in memoria, costanti o registri.
> 
> Costanti di tipo binario (0b000101), decimali (4289), esadecimali (0x69), ottali (0o263).
> 
> I puntatori alla memoria vengono dichiarati con le parentesi: (BX) oppure (var).
> 
> Si possono usare i registri a 1 o 2 byte (AX, BX...)
### Manipolazione dello stack
* `PUSH op` -> inserisce op nello stack;
* `POP [opzionale op]` -> fa il pop dallo stack, se è presente un operando carica il risultato del pop dentro.
### Operazioni matematiche
* `ADD(B) op1, op2` -> esegue l'addizione e poi memorizza il risultato su op1
* `SUB(B) op1, op2` -> esegue la sottrazione e poi memorizza il risultato su op1
* `MUL op` -> esegue la moltiplicazione fra AX e OP e poi memorizza il risultato su AX
* `MULB op` -> esegue la moltiplicazione fra AL e OP e poi memorizza il risultato su AL
* `DIV op` -> esegue la divisione fra AX e OP e poi memorizza il risultato su AX e il resto su DX
* `DIVB op` -> esegue la divisione fra AL e OP e poi memorizza il risultato su AL e il resto su AH
* `INC op` -> incrementa di 1 OP
* `DEC op` -> decrementa di 1 OP
### Operazioni logiche
* `AND op1, op2` -> esegue l'operazione AND fra OP1 e OP2 e poi memorizza il risultato su OP1
* `OR op1, op2` -> esegue l'operazione OR fra OP1 e OP2 e poi memorizza il risultato su OP1
* `NEG op` -> esegue l'operazione NOT su OP e poi memorizza il risultato su OP
* `XOR op1, op2` -> esegue l'operazione XOR fra OP1 e OP2 e poi memorizza il risultato su OP1
### Modifica al flusso del programma
* `LOOP etichetta` -> se il registro CX è maggiore o uguale a 0 fa un jump all'etichetta e decrementa CX
* `JMP etichetta` -> fa un salto incondizionato a quella etichetta
* `CMP op1, op2` -> esegue la comparazione fra OP1 e OP2
* `JCXZ etichetta` -> controlla se CX è uguale a 0 
* `JGE etichetta` -> se durante il precedente confronto $a>=b$ allora salta
* `JO etichetta` -> se durante il precedente confronto $a+b$ causa un overflow allora salta
* `JLE etichetta` -> se durante il precedente confronto $a<=b$ allora salta
* `JE etichetta` -> se durante il precedente confronto $a==b$ allora salta
* `JL etichetta` -> se durante il precedente confronto $a \l b$ allora salta
* `JG etichetta` -> se durante il precedente confronto $a \g b$ allora salta
* `JNE etichetta` -> se durante il precedente confronto $a!=b$ allora salta
* `CALL etichetta` -> chiama una funzione
### Chiamate al sistema operativo
* `SYS` -> esegue una syscall al sistema operativo. Le chiamate supportate sono printf, write (solo su stdout), getchar ed exit
### Gestione della memoria
* `MOV(B) op1, op2` -> copia OP2 in OP1
