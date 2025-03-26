# **Introdução** 

## **Spark** 

**Docs**: [https://spark.apache.org/docs/3.5.5/](https://spark.apache.org/docs/3.5.5/)

O **Apache Spark** é um mecanismo de computação distribuída de código aberto, projetado para o **processamento rápido e escalável de grandes volumes de dados**. Ele permite executar tarefas em cluster, distribuindo a carga de trabalho entre vários nós para maior eficiência e desempenho.

## **PySpark** 

**Docs**: [https://spark.apache.org/docs/latest/api/python/index.html](https://spark.apache.org/docs/latest/api/python/index.html)

**PySpark** é a API em Python para o Apache Spark, permitindo o processamento distribuído e escalável de grandes volumes de dados. Ele oferece suporte a Spark SQL, DataFrames, Machine Learning (MLlib) e Streaming, combinando a facilidade do Python com o poder do Spark.

## **Principais Recursos** 

**1\. Spark SQL e DataFrames**  
 O Spark SQL permite consultas a dados estruturados usando SQL ou Python, aproveitando o mesmo mecanismo de execução. Os DataFrames facilitam a manipulação, leitura e transformação de dados de forma eficiente.

**2\. API do Pandas no Spark**  
 Essa API escalona cargas de trabalho do pandas em nós distribuídos, facilitando a transição do pandas para o Spark sem modificar o código para lidar com grandes volumes de dados.

**3\. Structured Streaming**  
 Um mecanismo de processamento de streams tolerante a falhas, permitindo expressar computações de fluxo da mesma forma que o processamento em lote, com atualizações contínuas à medida que os dados chegam.

**4\. Machine Learning (MLlib)**  
 Uma biblioteca de aprendizado de máquina escalável, com APIs de alto nível para construção e ajuste de pipelines de ML.

**5\. Spark Core e RDDs**  
 A base do Spark, oferecendo RDDs e computação em memória. Embora os RDDs sejam flexíveis, os DataFrames são recomendados por otimizarem automaticamente as consultas.

**6\. Spark Streaming (Legado)**  
 Um mecanismo de streaming antigo, agora substituído pelo Structured Streaming para aplicações modernas de fluxo de dados.

O PySpark combina a facilidade do Python com a escalabilidade do Spark, tornando-o ideal para o processamento e análise de grandes volumes de dados.

# **SparkSQL** 

## **SparkSession** 

Docs: 

- [pyspark.sql.SparkSession](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.html)  
- [session.html\#SparkSession.builder](https://spark.apache.org/docs/latest/api/python/_modules/pyspark/sql/session.html#SparkSession.builder)

É o ponto de entrada para programar o Spark com a API Dataset e DataFrame. Um **SparkSession** pode ser usado para criar DataFrames, registrar DataFrames como tabelas, executar SQL sobre tabelas, armazenar tabelas em cache e ler arquivos Parquet. Para criar um **SparkSession**, use o seguinte padrão de construção:

```python
spark = (
    SparkSession.builder
        .master("local")
        .appName("Word Count")
        .config("spark.some.config.option", "some-value")
        .getOrCreate()
)
```

### **SparkSession.builder** 

O método `.builder` inicializa a configuração do Spark.

### **.appName** 

Define o nome da aplicação Spark. Isso é útil para identificar a execução no **Spark UI**.

### **.master** 

Define o **master URL**, que especifica onde o Spark será executado:

- `"local[*]"`: Executa localmente, usando todos os núcleos disponíveis.  
- `"spark://<host>:<port>"`: Conecta-se a um cluster Spark gerenciado. `7`

### **.getOrCreate¶**
getOrCreate**
Docs: [getOrCreate](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.builder.html#pyspark.sql.SparkSession.Builder.getOrCreate)  

Obtém uma SparkSession existente ou, se não houver uma, cria uma nova com base nas opções definidas neste construtor.

## **Leitura de arquivos**  

* **Extensibilidade:**  
   Novos formatos de arquivo ou opções adicionais podem estar disponíveis por meio de pacotes de terceiros. Sempre consulte a documentação do Spark 3.3.0 ou a documentação do pacote específico da fonte de dados para obter o conjunto mais preciso e completo de opções.  

* **Configuração vs. Opções de Leitura:**  
   Alguns comportamentos (como inferência de esquema, pushdown de predicados ou particionamento de arquivos) geralmente são controlados por configurações da sessão do Spark ou propriedades externas, em vez de opções passadas para o leitor.  

* **Encadeamento de Métodos:**  
   As opções geralmente são definidas de forma encadeada (ex.: `spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(path)`).  

### **Formato CSV**  

Docs: [https://spark.apache.org/docs/3.5.4/sql-data-sources-csv.html](https://spark.apache.org/docs/3.5.4/sql-data-sources-csv.html)  

Ao ler arquivos CSV (usando `spark.read.csv(...)` ou `spark.read.format("csv")`), as opções mais comuns incluem:  

* **`sep` / `delimiter`**  
   *Descrição:* Especifica o separador de colunas (padrão é a vírgula).  

* **`header`**  
   *Descrição:* Indica se a primeira linha do arquivo é um cabeçalho (padrão é false).  

* **`inferSchema`**  
   *Descrição:* Se definido como true, o Spark infere os tipos de dados das colunas a partir dos dados do arquivo (padrão é false).  

* **`charset`**  
   *Descrição:* Define a codificação de caracteres (padrão é “UTF-8”).  

* **`quote` & `escape`**  
   *Descrição:* Define o caractere de citação (padrão `"`); e o caractere de escape (padrão também é `"`).  

* **`multiLine`**  
   *Descrição:* Se true, permite que o arquivo tenha registros que se estendem por várias linhas (padrão é false).  

* **`mode`**  
   *Descrição:* Define o modo de análise ao encontrar registros malformados. Os valores típicos são `PERMISSIVE` (padrão), `DROPMALFORMED` ou `FAILFAST`.  

* **`nullValue` / `nanValue`**  
   *Descrição:* Especifica as representações em string para valores null ou NaN.  

* **`dateFormat` / `timestampFormat`**  
   *Descrição:* Personaliza o formato de análise para colunas de data e timestamp.  

Opções adicionais como `ignoreLeadingWhiteSpace`, `ignoreTrailingWhiteSpace`, `maxColumns` e `maxCharsPerColumn` também podem ser definidas.  

### **Formato JSON**  

Para arquivos JSON (`spark.read.json(...)` ou usando `.format("json")`), as opções disponíveis incluem:  

* **`multiLine`**  
   *Descrição:* Indica se os registros JSON se estendem por várias linhas (padrão é false).  

* **`allowComments`**  
   *Descrição:* Permite comentários no estilo Java/C++ dentro dos registros JSON (padrão é false).  

* **`allowSingleQuotes`** e **`allowUnquotedFieldNames`**  
   *Descrição:* Permitem analisar arquivos JSON que não seguem estritamente a convenção de aspas duplas para nomes de campos e strings.  

* **`primitivesAsString`**  
   *Descrição:* Se true, força todos os tipos primitivos a serem lidos como strings (padrão é false).  

* **`mode`**  
   *Descrição:* Especifica o modo de tratamento de erros (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`).  

* **`dateFormat` / `timestampFormat`**  
   *Descrição:* Define formatos para a análise de data e timestamp.  

* **`columnNameOfCorruptRecord`**  
   *Descrição:* Define o nome da coluna para armazenar registros malformados (padrão é “\_corrupt\_record”).  

* **`dropFieldIfAllNull`**  
   *Descrição:* Se true, remove um campo se todos os seus valores forem null.  

### **Formato Parquet**  

Para arquivos Parquet (`spark.read.parquet(...)` ou `.format("parquet")`), o número de opções personalizadas é mais limitado, pois o Parquet é um formato binário autodescritivo. As opções notáveis incluem:  

* **`mergeSchema`**  
   *Descrição:* Quando definido como true, mescla esquemas de diferentes arquivos Parquet (padrão é false).  

Outros comportamentos (como pushdown de predicados e poda de colunas) geralmente são configurados via configurações do Spark SQL em vez de opções de leitura individuais.  

### **Formato ORC**  

Para arquivos ORC (usando `.format("orc")` ou `spark.read.orc(...)`), as opções comuns incluem:  

* **`mergeSchema`**  
   *Descrição:* Semelhante ao Parquet, essa opção mescla esquemas de múltiplos arquivos ORC (padrão é false).  

Outras opções podem estar disponíveis, mas geralmente são menos numerosas do que para CSV ou JSON.  

### **Formato Texto**  

Ao ler arquivos de texto simples (com `.text(...)` ou `.format("text")`), as principais opções são:  

* **`wholetext`**  
   *Descrição:* Se definido como true, lê o arquivo inteiro como um único registro (padrão é false).  

* **`lineSep`**  
   *Descrição:* Especifica o caractere separador de linha (padrão é `\n`).  

### **Formato LibSVM**  

Para arquivos no formato LibSVM (usando `.format("libsvm")`), as seguintes opções são notáveis:  

* **`numFeatures`**  
   *Descrição:* (Opcional) Especifica explicitamente o número de features no conjunto de dados.  

* **`vectorType`**  
   *Descrição:* Determina a representação vetorial (geralmente “sparse” ou “dense”; padrão é “sparse”).  

### **Formato de Arquivo Binário**  

Ao ler arquivos binários via `.format("binaryFile")`, as opções incluem:  

* **`pathGlobFilter`**  
   *Descrição:* Um padrão glob para filtrar arquivos (ex.: `*.png`).  

* **`recursiveFileLookup`**  
   *Descrição:* Se true, busca arquivos recursivamente nos diretórios.  

* **`maxBytesPerFile`**  
   *Descrição:* Limita o número máximo de bytes lidos por arquivo.  

* **`modifiedBefore`** e **`modifiedAfter`**  
   *Descrição:* Filtram arquivos com base nos timestamps de modificação.  

### **Formato Avro (quando o suporte a Avro está habilitado)**  

Se o Spark for compilado com suporte a Avro (ou se o pacote apropriado for fornecido), arquivos Avro podem ser lidos usando `.format("avro")`. As opções incluem:  

* **`avroSchema`**  
   *Descrição:* Fornece um esquema Avro explícito como uma string JSON.  

* **`mode`**  
   *Descrição:* Determina a estratégia de tratamento de erros (como CSV/JSON).  

Outras opções específicas do Avro podem estar disponíveis dependendo da versão do Spark e do pacote utilizado.  

### **Formato Delta (com integração ao Delta Lake)**  

Embora não faça parte da distribuição principal do Spark, quando o Delta Lake é integrado, é possível ler tabelas Delta usando `.format("delta")`. Opções personalizadas incluem:  

* **`versionAsOf`**  
   *Descrição:* Lê uma versão específica de uma tabela Delta.  

* **`timestampAsOf`**  
   *Descrição:* Lê a tabela em um timestamp específico (habilita viagem no tempo). 

## Transformations

### pyspark.sql.DataFrame.toDF
Docs: [https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toDF.html](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toDF.html)<br>
DataFrame.toDF(*cols: str) → pyspark.sql.dataframe.DataFrame<br>
Returns a new DataFrame that with new specified column names


