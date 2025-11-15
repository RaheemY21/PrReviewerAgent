package com.repoInventory.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RepoInventoryRepository extends MongoRepository<RepoInventory, String> {

    // Custom query methods (optional)
    List<RepoInventory> findByLanguage(String language);

    List<RepoInventory> findByRepositoryContaining(String keyword);
}
