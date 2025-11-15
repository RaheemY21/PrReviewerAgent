package com.repoInventory.controller;


import com.repoInventory.repository.RepoInventory;
import com.repoInventory.repository.RepoInventoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/repo-inventory")
@CrossOrigin(origins = "*")
public class RepoInventoryController {

    @Autowired
    private RepoInventoryRepository repository;

    @GetMapping
    public ResponseEntity<List<RepoInventory>> getAllRepos() {
        try {
            List<RepoInventory> repos = repository.findAll();
            return new ResponseEntity<>(repos, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(null, HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<RepoInventory> getRepoById(@PathVariable String id) {
        Optional<RepoInventory> repo = repository.findById(id);
        return repo.map(value -> new ResponseEntity<>(value, HttpStatus.OK))
                .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    @PostMapping
    public ResponseEntity<RepoInventory> createRepo(@RequestBody RepoInventory repo) {
        try {
            repo.setCreatedAt(LocalDateTime.now());
            RepoInventory savedRepo = repository.save(repo);
            return new ResponseEntity<>(savedRepo, HttpStatus.CREATED);
        } catch (Exception e) {
            return new ResponseEntity<>(null, HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<RepoInventory> updateRepo(@PathVariable String id, @RequestBody RepoInventory repo) {
        Optional<RepoInventory> existingRepo = repository.findById(id);

        if (existingRepo.isPresent()) {
            RepoInventory updatedRepo = existingRepo.get();
            updatedRepo.setRepository(repo.getRepository());
            updatedRepo.setLanguage(repo.getLanguage());
            return new ResponseEntity<>(repository.save(updatedRepo), HttpStatus.OK);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<HttpStatus> deleteRepo(@PathVariable String id) {
        try {
            repository.deleteById(id);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @DeleteMapping
    public ResponseEntity<HttpStatus> deleteAllRepos() {
        try {
            repository.deleteAll();
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @GetMapping("/language/{language}")
    public ResponseEntity<List<RepoInventory>> getReposByLanguage(@PathVariable String language) {
        try {
            List<RepoInventory> repos = repository.findByLanguage(language);
            return new ResponseEntity<>(repos, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(null, HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
}