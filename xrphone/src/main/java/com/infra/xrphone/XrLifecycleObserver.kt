package com.infra.xrphone

import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner

class XrLifecycleObserver(
    private val onResume: () -> Unit,
    private val onPause: () -> Unit,
    private val onDestroy: () -> Unit
) : DefaultLifecycleObserver {

    override fun onResume(owner: LifecycleOwner) = onResume()
    override fun onPause(owner: LifecycleOwner) = onPause()
    override fun onDestroy(owner: LifecycleOwner) = onDestroy()
}
