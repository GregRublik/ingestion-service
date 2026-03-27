# INGESTION-SERVICE 
- Сервис для работы с документами, их загрузка и хранение в S3, а также сохранение metadata документов

```mermaid
graph TD
    K[evaluator-service] 
    
    
    C[orchestrator-service] <--1--> B[INGESTION-SERVICE]
    C <--2--> D[embedding-service]
    
    
    F[bot-service] --> c[orchestrator-service]  
    c <--1--> G[retrieval-service]
    c <--2--> E[reranker-service]
    c <--4--> I[generation-service]
    I --5--> F
    
    
    
    c <--Один и тот же оркестратор--> C
    
    style C fill:#f9f,stroke:#333,stroke-width:4px,color:#000
    style c fill:#f9f,stroke:#333,stroke-width:4px,color:#000
    style B fill:#bbf,stroke:#f66,stroke-width:2px,color:#000
    
```
