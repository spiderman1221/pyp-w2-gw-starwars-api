from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError
import six

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key,value in six.iteritems(json_data):
            setattr(self, key, value)
        

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        # let's generate the method name dynamically based
        # on the RESOURCE_NAME class variable
        method_name = 'get_{}'.format(cls.RESOURCE_NAME)  # this will be either `get_people` or `get_films`
    
        # now that we have the name, let's pick the actual method function
        # from the `api_client` object using the built-in `getattr()`
        method = getattr(api_client, method_name)
    
        # and finally let's execute the method sending the proper parameters
        # and return the result
        json_data = method(resource_id)
    
        # remember that the result of the `get()` method must be an instance
        # of the model. That's why we need to instantiate `cls`, which
        # represents the current Model class (either People or Films)
        return cls(json_data)
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        
        name = ('{}QuerySet').format(cls.RESOURCE_NAME.title())
        return eval(name)()
        
        
    """So, thinking People
        .all(), needs to give us both key and value 
        and then somehow we need a next ability that will pick up 
        both key and value and give themto us. So People.all needs to push
        us towards the PeopleQuery, which then pushes us towards Basequery"""


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.current_page = 0
        self.current_element = 0
        self.objects = []
        self.counter = None
    def __iter__(self):
        return self.__class__()

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if self.current_element + 1 > len(self.objects):
            # need to request a new page
                try:
                    self._request_next_page()
                except SWAPIClientError:
                    raise StopIteration()
            elem = self.objects[self.current_element]
            self.current_element += 1
            return elem
    next = __next__
    def _request_next_page(self):
        """
        Requests next page of elements to the API based on the current state
        of the iteration.
        """
        # increate the page counter to request the following page
        self.current_page += 1
    
        # request next page in a generic way. Similar to what we did in BaseModel
        method_name = 'get_{}'.format(self.RESOURCE_NAME)
        method = getattr(api_client, method_name)
        json_data = method(**{'page': self.current_page})
        self.counter = json_data['count']
        #method_name = 'get_{}'.format(self.RESOURCE_NAME)
        ###method = getattr(api_client, method_name)
        ###json_data = method(resource_id)
    
        # remember that each element in `self.objects` needs to be an instance
        # of the proper Model class. For that we will instantiate the Model class
        # (either People or Films) for each result in the new page.
        Model = eval(self.RESOURCE_NAME.title())
        for resource_data in json_data['results']:
            self.objects.append(Model(resource_data))
        

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        if self.counter is None:
            self._request_next_page()
        return self.counter
        
        
        
    
        

class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
