"""Background tasks service for async processing."""
from typing import Dict, Any, Callable
import asyncio
from datetime import datetime


class BackgroundTasksService:
    """Service for handling background tasks."""
    
    def __init__(self):
        """Initialize background tasks service."""
        self.tasks = {}
        self.task_results = {}
    
    async def schedule_analysis(
        self,
        task_id: str,
        log_data: Dict[str, Any],
        analysis_func: Callable,
        callback: Callable = None
    ) -> str:
        """
        Schedule an analysis task to run in background.
        
        Args:
            task_id: Unique task identifier
            log_data: Log data to analyze
            analysis_func: Async function to run analysis
            callback: Optional callback function after analysis completes
            
        Returns:
            Task ID
        """
        task = asyncio.create_task(self._run_analysis(task_id, log_data, analysis_func, callback))
        self.tasks[task_id] = {
            'task': task,
            'status': 'running',
            'started_at': datetime.now()
        }
        return task_id
    
    async def _run_analysis(
        self,
        task_id: str,
        log_data: Dict[str, Any],
        analysis_func: Callable,
        callback: Callable = None
    ):
        """Run analysis task."""
        try:
            result = await analysis_func(log_data)
            self.task_results[task_id] = {
                'status': 'completed',
                'result': result,
                'completed_at': datetime.now()
            }
            
            if callback:
                await callback(task_id, result)
                
        except Exception as e:
            self.task_results[task_id] = {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now()
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a background task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status dictionary
        """
        if task_id in self.task_results:
            return self.task_results[task_id]
        elif task_id in self.tasks:
            return {
                'status': self.tasks[task_id]['status'],
                'started_at': self.tasks[task_id]['started_at']
            }
        else:
            return {'status': 'not_found'}
    
    def list_tasks(self) -> Dict[str, Any]:
        """List all background tasks."""
        return {
            'running': [tid for tid, info in self.tasks.items() if info['status'] == 'running'],
            'completed': list(self.task_results.keys())
        }
