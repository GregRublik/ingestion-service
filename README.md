# INGESTION-SERVICE 
- Сервис для работы с документами, их загрузка и хранение в S3, а также сохранение metadata документов

```mermaid
graph TD
        
    C[orchestrator-service] --1--> B[INGESTION-SERVICE]
    C --2---> D[embedding-service]
    
    
    F[bot-service] --1--> c[orchestrator-service]  
    c --2--> G[retrieval-service]
    G --3--> E[reranker-service]
    E --4--> I[generation-service]
    I --5--> F
    
    c <--Один и тот же оркестратор--> C


    style C fill:#f9f,stroke:#333,stroke-width:4px,color:#000
    style c fill:#f9f,stroke:#333,stroke-width:4px,color:#000
    style B fill:#bbf,stroke:#f66,stroke-width:2px,color:#000
    
```
    

orchestrator-service

bot-service 

retrieval-service 
reranker-service

evaluator-service

generation-service

ingestion-service 
embedding-service

