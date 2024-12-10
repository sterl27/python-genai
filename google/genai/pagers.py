# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Pagers for the GenAI List APIs."""

# pylint: disable=protected-access

import copy
from typing import Any, AsyncIterator, Awaitable, Callable, Generic, Iterator, Literal, TypeVar

T = TypeVar('T')

PagedItem = Literal[
    'batch_jobs', 'models', 'tuning_jobs', 'files', 'cached_contents'
]


class _BasePager(Generic[T]):
  """Base pager class for iterating through paginated results."""

  def __init__(
      self,
      name: PagedItem,
      request: Callable[Any, Any],
      response: Any,
      config: Any,
  ):
    self._name = name
    self._request = request

    self._page = getattr(response, self._name) or []
    self._idx = 0

    if not config:
      request_config = {}
    elif isinstance(config, dict):
      request_config = copy.deepcopy(config)
    else:
      request_config = dict(config)
    request_config['page_token'] = getattr(response, 'next_page_token')
    self._config = request_config

    self._page_size = request_config.get('page_size', len(self._page))

  @property
  def page(self) -> list[T]:
    """Returns the current page, which is a list of items.

    The returned list of items is a subset of the entire list.

    Usage:

    .. code-block:: python

      batch_jobs_pager = client.batches.list(config={'page_size': 5})
      print(f"first page: {batch_jobs_pager.page}")
      # first page: [BatchJob(name='projects/./locations/./batchPredictionJobs/1
    """

    return self._page

  @property
  def name(self) -> str:
    """Returns the type of paged item (for example, ``batch_jobs``).

    Usage:

    .. code-block:: python

      batch_jobs_pager = client.batches.list(config={'page_size': 5})
      print(f"name: {batch_jobs_pager.name}")
      # name: batch_jobs
    """

    return self._name

  @property
  def page_size(self) -> int:
    """Returns the length of the page fetched each time by this pager.

    The number of items in the page is less than or equal to the page length.

    Usage:

    .. code-block:: python

      batch_jobs_pager = client.batches.list(config={'page_size': 5})
      print(f"page_size: {batch_jobs_pager.page_size}")
      # page_size: 5
    """

    return self._page_size

  @property
  def config(self) -> dict[str, Any]:
    """Returns the configuration when making the API request for the next page.

    A configuration is a set of optional parameters and arguments that can be
    used to customize the API request. For example, the ``page_token`` parameter
    contains the token to request the next page.

    Usage:

    .. code-block:: python

      batch_jobs_pager = client.batches.list(config={'page_size': 5})
      print(f"config: {batch_jobs_pager.config}")
      # config: {'page_size': 5, 'page_token': 'AMEw9yO5jnsGnZJLHSKDFHJJu'}
    """

    return self._config

  def __len__(self) -> int:
    """Returns the total number of items in the current page."""
    return len(self.page)

  def __getitem__(self, index: int) -> T:
    """Returns the item at the given index."""
    return self.page[index]

  def _init_next_page(self, response: Any) -> None:
    """Initializes the next page from the response.

    This is an internal method that should be called by subclasses after
    fetching the next page.

    Args:
      response: The response object from the API request.
    """
    self.__init__(self.name, self._request, response, self.config)


class Pager(_BasePager[T]):
  """Pager class for iterating through paginated results."""

  def __next__(self) -> T:
    """Returns the next item."""
    if self._idx >= len(self):
      try:
        self.next_page()
      except IndexError:
        raise StopIteration

    item = self.page[self._idx]
    self._idx += 1
    return item

  def __iter__(self) -> Iterator[T]:
    """Returns an iterator over the items."""
    self._idx = 0
    return self

  def next_page(self) -> list[T]:
    """Fetches the next page of items. This makes a new API request.

    Usage:

    .. code-block:: python

      batch_jobs_pager = client.batches.list(config={'page_size': 5})
      print(f"current page: {batch_jobs_pager.page}")
      batch_jobs_pager.next_page()
      print(f"next page: {batch_jobs_pager.page}")
      # current page: [BatchJob(name='projects/.../batchPredictionJobs/1
      # next page: [BatchJob(name='projects/.../batchPredictionJobs/6
    """

    if not self.config.get('page_token'):
      raise IndexError('No more pages to fetch.')

    response = self._request(config=self.config)
    self._init_next_page(response)
    return self.page


class AsyncPager(_BasePager[T]):
  """AsyncPager class for iterating through paginated results."""

  def __init__(
      self,
      name: PagedItem,
      request: Callable[Any, Awaitable[Any]],
      response: Any,
      config: Any,
  ):
    super().__init__(name, request, response, config)

  def __aiter__(self) -> AsyncIterator[T]:
    """Returns an async iterator over the items."""
    self._idx = 0
    return self

  async def __anext__(self) -> Awaitable[T]:
    """Returns the next item asynchronously."""
    if self._idx >= len(self):
      try:
        await self.next_page()
      except IndexError:
        raise StopAsyncIteration

    item = self.page[self._idx]
    self._idx += 1
    return item

  async def next_page(self) -> list[T]:
    """Fetches the next page of items asynchronously.

    This makes a new API request.

    Returns:
      The next page of items.

    Raises:
      IndexError: No more pages to fetch.

    Usage:

    .. code-block:: python

      batch_jobs_pager = await client.aio.batches.list(config={'page_size': 5})
      print(f"current page: {batch_jobs_pager.page}")
      await batch_jobs_pager.next_page()
      print(f"next page: {batch_jobs_pager.page}")
      # current page: [BatchJob(name='projects/.../batchPredictionJobs/1
      # next page: [BatchJob(name='projects/.../batchPredictionJobs/6
    """

    if not self.config.get('page_token'):
      raise IndexError('No more pages to fetch.')

    response = await self._request(config=self.config)
    self._init_next_page(response)
    return self.page