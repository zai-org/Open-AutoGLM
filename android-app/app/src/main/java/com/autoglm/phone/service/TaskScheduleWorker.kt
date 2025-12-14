package com.autoglm.phone.service

import android.content.Context
import android.content.Intent
import androidx.work.*
import com.autoglm.phone.data.ScheduledTask
import com.autoglm.phone.data.ScheduledTaskRepository
import kotlinx.coroutines.flow.first
import java.util.Calendar
import java.util.concurrent.TimeUnit

/**
 * Worker that executes scheduled tasks.
 */
class TaskScheduleWorker(
    context: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(context, workerParams) {
    
    override suspend fun doWork(): Result {
        val taskId = inputData.getString(KEY_TASK_ID) ?: return Result.failure()
        val prompt = inputData.getString(KEY_PROMPT) ?: return Result.failure()
        
        android.util.Log.d("TaskScheduleWorker", "Executing scheduled task: $taskId")
        
        try {
            // Start TaskExecutionService to run the task
            val intent = Intent(applicationContext, TaskExecutionService::class.java).apply {
                action = TaskExecutionService.ACTION_START_TASK
                putExtra(TaskExecutionService.EXTRA_TASK, prompt)
            }
            applicationContext.startService(intent)
            
            // Update last run time
            val repository = ScheduledTaskRepository(applicationContext)
            val tasks = repository.scheduledTasks.first()
            val task = tasks.find { it.id == taskId }
            if (task != null) {
                repository.updateTask(task.copy(
                    lastRunTime = System.currentTimeMillis(),
                    lastResult = "已执行"
                ))
            }
            
            return Result.success()
        } catch (e: Exception) {
            android.util.Log.e("TaskScheduleWorker", "Failed to execute task: ${e.message}")
            return Result.failure()
        }
    }
    
    companion object {
        const val KEY_TASK_ID = "task_id"
        const val KEY_PROMPT = "prompt"
        
        /**
         * Schedule a task to run at specified time.
         */
        fun scheduleTask(context: Context, task: ScheduledTask) {
            val workManager = WorkManager.getInstance(context)
            
            // Calculate initial delay
            val now = Calendar.getInstance()
            val targetTime = Calendar.getInstance().apply {
                set(Calendar.HOUR_OF_DAY, task.hour)
                set(Calendar.MINUTE, task.minute)
                set(Calendar.SECOND, 0)
                set(Calendar.MILLISECOND, 0)
            }
            
            // If target time is in the past, schedule for tomorrow
            if (targetTime.before(now)) {
                targetTime.add(Calendar.DAY_OF_MONTH, 1)
            }
            
            val initialDelay = targetTime.timeInMillis - now.timeInMillis
            
            val inputData = workDataOf(
                KEY_TASK_ID to task.id,
                KEY_PROMPT to task.prompt
            )
            
            // Create periodic work request (daily)
            val workRequest = PeriodicWorkRequestBuilder<TaskScheduleWorker>(
                1, TimeUnit.DAYS
            )
                .setInitialDelay(initialDelay, TimeUnit.MILLISECONDS)
                .setInputData(inputData)
                .addTag(getWorkTag(task.id))
                .setConstraints(
                    Constraints.Builder()
                        .setRequiresBatteryNotLow(false)
                        .build()
                )
                .build()
            
            workManager.enqueueUniquePeriodicWork(
                getWorkName(task.id),
                ExistingPeriodicWorkPolicy.UPDATE,
                workRequest
            )
            
            android.util.Log.d("TaskScheduleWorker", 
                "Scheduled task ${task.id} for ${task.hour}:${task.minute}, initial delay: ${initialDelay / 1000 / 60} minutes")
        }
        
        /**
         * Cancel a scheduled task.
         */
        fun cancelTask(context: Context, taskId: String) {
            val workManager = WorkManager.getInstance(context)
            workManager.cancelUniqueWork(getWorkName(taskId))
            android.util.Log.d("TaskScheduleWorker", "Cancelled task: $taskId")
        }
        
        private fun getWorkName(taskId: String) = "scheduled_task_$taskId"
        private fun getWorkTag(taskId: String) = "task_$taskId"
    }
}
