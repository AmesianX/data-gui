"""
Copyright (C) 2018 IAIK TU Graz (data@iaik.tugraz.at)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

@version 1.1

"""

from PyQt5.QtCore import Qt, QVariant, QModelIndex
from datastub.leaks import CallHistory
from datastub.utils import sorted_keys

from datagui.package.model.BaseTreeItem import BaseTreeItem
from datagui.package.model.BaseTreeModel import BaseTreeModel
from datagui.package.utils import CustomRole, CustomType, getCtxName


class CallHierarchyItem(BaseTreeItem):
    id = -1

    def __init__(self, name, obj=None, parent=None):
        super(CallHierarchyItem, self).__init__(name, obj, parent)
        self.id = CallHierarchyItem.id = CallHierarchyItem.id + 1

    def type(self):
        return CustomType.callHierarchyItem

    def __copy__(self):
        # Note: Does not copy child_items. Is this a problem??
        new_item = CallHierarchyItem(self.name, self.obj, self.parent_item)
        new_item.id = self.id
        assert(new_item.parent_item == self.parent_item)
        return new_item

class CallHierarchyModel(BaseTreeModel):

    def __init__(self, call_hierarchy=None):
        super(CallHierarchyModel, self).__init__()
        self.root_item = None

        if call_hierarchy is not None:
            assert isinstance(call_hierarchy, CallHistory)
            self.setupData(call_hierarchy)

    # # # # # # # # # # # # #
    # OVERLOADED FUNCTIONS  #
    # # # # # # # # # # # # #

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(Qt.DisplayRole, index.column())
        elif role == CustomRole.Obj:
            item = index.internalPointer()
            return item.data(CustomRole.Obj)
        elif role == CustomRole.Ip:
            item = index.internalPointer()
            return item.data(CustomRole.Ip)
        elif role == CustomRole.Id:
            item = index.internalPointer()
            return item.id
        elif role == CustomRole.CallItem:
            return index.internalPointer()
        else:
            return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            parent_item = parent.internalPointer()
        else:
            parent_item = self.root_item

        child_item = parent_item.child_items[row]
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return len(parent_item.child_items)

    # # # # # # # # #
    # MY FUNCTIONS  #
    # # # # # # # # #

    def setupData(self, call_hierarchy, parent=None):
        if call_hierarchy is None:
            return None

        if call_hierarchy.parent is None:
            self.root_item = CallHierarchyItem("Call Hierarchy", call_hierarchy)
            self.setupData(call_hierarchy.children[next(iter(call_hierarchy.children))], self.root_item)
        else:
            call_hierarchy_item = CallHierarchyItem("{}".format(getCtxName(call_hierarchy.ctxt.callee)),
                                                    call_hierarchy, parent)

            parent.appendChild(call_hierarchy_item)

            parent = call_hierarchy_item
            for k in sorted_keys(call_hierarchy.children):
                self.setupData(call_hierarchy.children[k], parent)
