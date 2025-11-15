package com.repoInventory.repository;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "repoInventory")
public class RepoInventory {

    @Id
    private String id;

    private String repository;

    private String language;

    private LocalDateTime createdAt;

    public RepoInventory(String repository, String language) {
        this.repository = repository;
        this.language = language;
        this.createdAt = LocalDateTime.now();
    }
}