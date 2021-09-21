# home-work-11

Flask version of personal assistant.

New features added: blueprints, authentification, HTML templates inheritance.

Inline with given recomendations: 

 - all the functions, that work with database wrapped with LRU cache, organized LRU cache invalidation on insert/update operations 
 
 - abstract classes used for database interface: user could choose what DB engine would be use for storing data (Mongo or Postgres)
  
 To run upp: 
  
  export FLASK_APP=__init__.py:init_app()
  
  export FLASK_ENV=development
  
  flask run
