# Dependencies and scope — checked 2026-10-08

| Component | Selected baseline | Note |
|---|---|---|
| Python | 3.11 image | Host checks may use Python 3.12; record exact test environment separately |
| Spark / Delta | 3.5.6 / 3.3.2 | Matched compatibility families; Scala 2.12 connector |
| Kafka | 3.9.1 official Apache image | One KRaft broker; no HA |
| Hadoop S3A | 3.3.4 | Match bundled Hadoop family, avoid arbitrary AWS SDK JAR substitutions |
| Airflow | 3.3.2, Python 3.11 | Official constraints pin provider dependencies; standalone development mode in one pod |
| PostgreSQL | 16.8 | Airflow metadata only |
| MinIO | Source tag RELEASE.2025-10-15T17-29-55Z | Built with Go 1.24.8; archived community software; isolated lab only |
| React / Vite | 18.3.1 / 6.1.0 | npm lock included; inspect audit output before any public deployment |
| kind / kubectl | User-installed compatible versions | Record installed versions and image digests after first successful local deployment |

Direct Python pins and npm lock are supplied; this is not a fully hermetic artifact. Base-image tags, OS package indexes and Maven resolution still require a first-build lock/digest capture. No dependency binaries are bundled in the ZIP. No paid license key or expiring credit is required.

Official references:

- [MinIO repository status and source distribution](https://github.com/minio/minio)
- [MinIO pinned release](https://github.com/minio/minio/releases/tag/RELEASE.2025-10-15T17-29-55Z)
- [Airflow installation](https://airflow.apache.org/docs/apache-airflow/stable/installation.html)
- [KubernetesPodOperator](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html)
- [LocalExecutor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/local.html)
- [Airflow database setup](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html)
- [SimpleAuthManager](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/auth-manager/simple/index.html)
- [Delta/Spark compatibility](https://docs.delta.io/releases/)
- [kind quickstart and image loading](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Spark Kafka source](https://spark.apache.org/docs/3.5.6/structured-streaming-kafka-integration.html)

MinIO is AGPLv3. Keep its source/license obligations distinct from application code and other dependency licenses. The code archive contains a build recipe, not a redistributed MinIO binary. Do not assume the archived project receives future security fixes. ClusterIP services and localhost port forwarding are deliberate lab boundaries; this package is not a public hardened deployment.
