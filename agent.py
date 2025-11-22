import os
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import git
from git import Repo, GitCommandError
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoDBRepositoryAgent:
    """Agent to manage MongoDB connections and Git repository operations"""
    
    def __init__(self, 
                 username: str, 
                 password: str, 
                 hosts: List[str],
                 database: str,
                 replica_set: str = "rs_d0dpst",
                 auth_mechanism: str = "PLAIN",
                 auth_source: str = "$external"):
        """
        Initialize the MongoDB Repository Agent
        
        Args:
            username: MongoDB username
            password: MongoDB password
            hosts: List of MongoDB host:port strings
            database: Database name
            replica_set: Replica set name
            auth_mechanism: Authentication mechanism
            auth_source: Authentication source
        """
        self.username = username
        self.password = password
        self.hosts = hosts
        self.database = database
        self.replica_set = replica_set
        self.auth_mechanism = auth_mechanism
        self.auth_source = auth_source
        self.client: Optional[MongoClient] = None
        self.db = None
        
    def build_connection_uri(self) -> str:
        """Build MongoDB connection URI"""
        # URL encode username and password
        encoded_username = quote_plus(self.username)
        encoded_password = quote_plus(self.password)
        
        # Join hosts
        hosts_str = ",".join(self.hosts)
        
        # Build URI
        uri = (f"mongodb://{encoded_username}:{encoded_password}@{hosts_str}/"
               f"?replicaSet={self.replica_set}"
               f"&authMechanism={self.auth_mechanism}"
               f"&authSource={self.auth_source}")
        
        return uri
    
    def connect(self) -> bool:
        """
        Connect to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            uri = self.build_connection_uri()
            logger.info("Connecting to MongoDB...")
            
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database]
            
            logger.info(f"Successfully connected to database: {self.database}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def get_repositories(self, collection_name: str = "repos") -> List[Dict]:
        """
        Fetch repository URLs from MongoDB collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of repository documents
        """
        try:
            if not self.db:
                logger.error("Not connected to database")
                return []
            
            collection = self.db[collection_name]
            repos = list(collection.find({}))
            
            logger.info(f"Found {len(repos)} repositories in collection '{collection_name}'")
            return repos
            
        except OperationFailure as e:
            logger.error(f"Failed to fetch repositories: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching repositories: {e}")
            return []
    
    def clone_and_create_branch(self, 
                                repo_url: str, 
                                branch_name: str = "orchestra-update",
                                git_username: Optional[str] = None,
                                git_token: Optional[str] = None) -> bool:
        """
        Clone repository and create a new branch
        
        Args:
            repo_url: Repository URL
            branch_name: Name of the branch to create
            git_username: Git username for authentication (optional)
            git_token: Git token/password for authentication (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Cloning repository: {repo_url}")
            
            # Prepare URL with authentication if provided
            clone_url = repo_url
            if git_username and git_token:
                # Parse and rebuild URL with credentials
                if repo_url.startswith('https://'):
                    clone_url = repo_url.replace('https://', 
                                                 f'https://{git_username}:{git_token}@')
            
            # Clone repository
            repo = Repo.clone_from(clone_url, temp_dir)
            logger.info(f"Repository cloned to: {temp_dir}")
            
            # Check if branch already exists
            if branch_name in [ref.name.split('/')[-1] for ref in repo.refs]:
                logger.warning(f"Branch '{branch_name}' already exists locally")
                
                # Check if it exists on remote
                try:
                    repo.git.fetch('origin', branch_name)
                    logger.warning(f"Branch '{branch_name}' already exists on remote")
                    return False
                except GitCommandError:
                    logger.info(f"Branch '{branch_name}' doesn't exist on remote, will create")
            
            # Create and checkout new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            logger.info(f"Created and checked out branch: {branch_name}")
            
            # Push branch to remote
            origin = repo.remote('origin')
            origin.push(refspec=f'{branch_name}:{branch_name}')
            logger.info(f"Pushed branch '{branch_name}' to remote")
            
            return True
            
        except GitCommandError as e:
            logger.error(f"Git error for {repo_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error processing {repo_url}: {e}")
            return False
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_dir}: {e}")
    
    def process_all_repositories(self, 
                                 collection_name: str = "repos",
                                 url_field: str = "url",
                                 branch_name: str = "orchestra-update",
                                 git_username: Optional[str] = None,
                                 git_token: Optional[str] = None) -> Dict[str, int]:
        """
        Process all repositories from MongoDB collection
        
        Args:
            collection_name: Name of the MongoDB collection
            url_field: Field name containing repository URL
            branch_name: Name of branch to create
            git_username: Git username for authentication
            git_token: Git token for authentication
            
        Returns:
            Dictionary with success and failure counts
        """
        repos = self.get_repositories(collection_name)
        results = {"success": 0, "failed": 0, "total": len(repos)}
        
        for repo_doc in repos:
            repo_url = repo_doc.get(url_field)
            if not repo_url:
                logger.warning(f"Repository document missing '{url_field}' field: {repo_doc.get('_id')}")
                results["failed"] += 1
                continue
            
            logger.info(f"\nProcessing repository: {repo_url}")
            success = self.clone_and_create_branch(
                repo_url, 
                branch_name,
                git_username,
                git_token
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing complete!")
        logger.info(f"Total repositories: {results['total']}")
        logger.info(f"Successful: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"{'='*60}")
        
        return results
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def main():
    """Main execution function"""
    
    # Configuration - Update these values
    MONGO_CONFIG = {
        'username': 'UserName',
        'password': 'Password',
        'hosts': ['host1', 'host2'],
        'database': 'database_name',
        'replica_set': 'replica'
    }
    
    # Git credentials (optional - set these if repositories require authentication)
    GIT_USERNAME = os.getenv('GIT_USERNAME')  # or set directly
    GIT_TOKEN = os.getenv('GIT_TOKEN')  # or set directly
    
    # Collection and field configuration
    COLLECTION_NAME = 'repos'
    URL_FIELD = 'url'  # Adjust based on your document structure
    BRANCH_NAME = 'orchestra-update'
    
    # Create agent
    agent = MongoDBRepositoryAgent(**MONGO_CONFIG)
    
    try:
        # Connect to MongoDB
        if not agent.connect():
            logger.error("Failed to connect to MongoDB. Exiting.")
            return
        
        # Process all repositories
        results = agent.process_all_repositories(
            collection_name=COLLECTION_NAME,
            url_field=URL_FIELD,
            branch_name=BRANCH_NAME,
            git_username=GIT_USERNAME,
            git_token=GIT_TOKEN
        )
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    finally:
        agent.disconnect()


if __name__ == "__main__":
    main()
